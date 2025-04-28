import re
from db import *
from config import *
from time import sleep
from db.models import *
from LLM.models import *
from core.converter import Converter
from typing import Tuple, List, Optional
from ui.ui_interactor import UIInteractor
from core.image_handler import ImageHandler
from mocks.response_mock import ResponseMock
from geoguessr.client import GeoGuessrClient
from langchain_core.messages import AIMessage
from LLM.prompt_composer import PromptComposer
from ui.browser_interactor import BrowserInteractor

class GeoAgent:
    def __init__(self, keypoints: dict, LLMs: List[Tuple[LLM_type, str]], rounds_number: int = ROUNDS_NUMBER):
        self.rounds_number = rounds_number
        self.image_handler = ImageHandler()
        self.prompt_composer = PromptComposer()
        self.geoguessr_client = GeoGuessrClient()
        self.interactor = UIInteractor(keypoints)
        self.models_db_ids = self._get_db_models_ids(LLMs)
        self.converter = Converter(keypoints, self.interactor)
        self.LLMs = [model_type(model=model_name) for model_type, model_name in LLMs]

    def _get_db_models_ids(self, LMMs: List[Tuple[LLM_type, str]]) -> List[int]:
        models_ids = []

        for vendor_class, model_name in LMMs:
            vendor = Vendor()
            vendor.name = vendor_class.__name__
            vendor_db = vendor_repo.add_vendor_if_not_exists(vendor)

            model = Model()
            model.vendor_id = vendor_db.id
            model.model_name = model_name
            model_db = model_repo.add_model_if_not_exists(model)

            models_ids.append(model_db.id)
        
        return models_ids

    def _get_geolocation_from_response(self, llm_response: AIMessage) -> Optional[Tuple[float, float]]:
        try:
            match = re.search(r"lat:\s*(-?\d+\.\d+),\s*lng:\s*(-?\d+\.\d+)", llm_response.content.lower())
            if match is None: return None
            lat = float(match.group(1))
            lng = float(match.group(2))
            return lat, lng
        except Exception as e:
            print("Error while parsing LLM response:", e)
            return None

    def _aggregate_model_geolocations(self, responses: List[AIMessage]) -> Optional[Tuple[float, float]]:
        coords = []
        for i, response in enumerate(responses):
            print(f"\n~ ~ ~ {type(self.LLMs[i]).__name__} 's response ~ ~ ~")
            print(response.content)
            geolocation = self._get_geolocation_from_response(response)
            if geolocation:
                coords.append(geolocation)
        if not coords:
            return None
        lat = sum([c[0] for c in coords]) / len(coords)
        lng = sum([c[1] for c in coords]) / len(coords)
        return lat, lng

    def _play_round(self, round_number: int) -> None:        
        screenshot = self.interactor.take_image_screenshot()
        self.image_handler.set_image(screenshot)
        self.image_handler.preprocess()
        screenshot_b64 = self.image_handler.convert_to_base64()

        message = self.prompt_composer.compose_prompt([screenshot_b64])

        image_path = image_repo.save_image(self.image_handler.image, self.game_id, round_number)

        game_data = self.geoguessr_client.get_game_data(self.game_id)
        round_db_initial = self._compose_initial_round_db_entity(game_data, round_number)
        round_db_initial = round_repo.add_round(round_db_initial)
        round_db_initial.round_image_url = image_path

        geolocation = None
        retries = 0
        while geolocation is None and retries <= LLM_RETRY_LIMIT:
            print(f"Attempt {retries + 1} to get geolocation...")
            responses = [llm.invoke([message]) for llm in self.LLMs]
            # responses = [ResponseMock(), ResponseMock((20, 20)), ResponseMock((30, 0))]
            geolocation = self._aggregate_model_geolocations(responses)
            retries += 1
        
        for index, llm_reponse in enumerate(responses):
            guess = Guess()
            guess.round_id = round_db_initial.id
            guess.model_id = self.models_db_ids[index]
            guess.reasoning = llm_reponse.content
            guess.seconds_spent = 10 # temp stub
            try:
                geolocation = self._get_geolocation_from_response(llm_reponse)
                guess.predicted_latitude = geolocation[0]
                guess.predicted_longitude = geolocation[1]
            except:
                guess.predicted_latitude = None
                guess.predicted_longitude = None
            guess_db = guess_repo.add_guess(guess)

        if geolocation is None:
            print(f"\nFailed to get a geolocation after {LLM_RETRY_LIMIT} retries.")
            geolocation = [1, 1]
        else:
            print(f"\nPredicted geolocation (aggregated): lat: {geolocation[0]}, lng: {geolocation[1]}")

        map_x, map_y = self.converter.geolocation_to_map_coordinates(*geolocation)
        print(f"Map coordinates before correction: x: {map_x}, y: {map_y}")

        self.interactor.hover_over_map()

        map_x, map_y = self.converter.adjust_map_coordinates(map_x, map_y)
        map_x, map_y = self.converter.clip_map_coordinates(map_x, map_y)
        print(f"Map coordinates after correction: x: {map_x}, y: {map_y}")

        self.interactor.click_on_position(map_x, map_y)
        self.interactor.click_on_confirm()
        self.interactor.move_away_from_map()
        self.interactor.go_to_next_round()

        game_data = self.geoguessr_client.get_game_data(self.game_id)
        round_db_final = self._finalize_round_db_entity(round_db_initial, game_data)
        round_db_final = round_repo.update_round(round_db_final)

    def _compose_initial_round_db_entity(self, game_data, round_number: int) -> Round:
        round_db = Round()
        round_db.game_token = self.game_id
        round_db.round_number = round_number

        last_round_available = game_data["rounds"][-1]

        round_db.true_latitude = last_round_available["lat"]
        round_db.true_longitude = last_round_available["lng"]

        round_db.panorama_id = last_round_available["panoId"]

        round_db.country_code = last_round_available["streakLocationCode"]

        return round_db

    def _finalize_round_db_entity(self, round_db: Round, game_data) -> Round:
        last_guess_available = game_data["player"]["guesses"][-1]

        round_db.score = last_guess_available["roundScoreInPoints"]
        round_db.distance_km = last_guess_available["distanceInMeters"] / 100
        round_db.aggregated_latitude = last_guess_available["lat"]
        round_db.aggregated_longitude = last_guess_available["lng"]

        print(f"Put geolocation: lat: {round_db.aggregated_latitude}, lng: {round_db.aggregated_longitude}")

        return round_db

    def _compose_initial_game_db_entity(self, game_data) -> Game:
        game_db = Game()
        game_db.token = game_data["token"]
        game_db.map = game_data["map"]
        game_db.player_id = game_data["player"]["id"]
        return game_db

    def _finalize_game_db_entity(self, game_db: Game, game_data) -> Game:
        game_db.rounds_count = game_data["round"]
        game_db.total_score = int(game_data["player"]["totalScore"]["amount"])
        game_db.total_distance_km = game_data["player"]["totalDistanceInMeters"] / 1000
        return game_db
    
    def run(self) -> None:
        browser_interactor = BrowserInteractor()
        self.game_id = browser_interactor.get_game_id()

        game_data = self.geoguessr_client.get_game_data(self.game_id)
        game_db_initial = self._compose_initial_game_db_entity(game_data)
        game_db_initial = game_repo.add_game(game_db_initial)

        for round in range(self.rounds_number):
            print(f"\n ~ ~ ~ Round {round+1}/{ROUNDS_NUMBER} ~ ~ ~")
            sleep(PRE_ROUND_DELAY)
            self._play_round(round + 1)
        
        game_data = self.geoguessr_client.get_game_data(self.game_id)
        game_db_final = self._finalize_game_db_entity(game_db_initial, game_data)
        game_db_final = game_repo.update_game(game_db_final)