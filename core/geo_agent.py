from db import *
from LLM import *
from config import *
from time import sleep
from typing import Tuple, List
from LLM import LlmGuess, LlmWrapper
from core.geolocation import Geolocation
from ui.ui_interactor import UIInteractor
from core.image_handler import ImageHandler
from core.geo_map_helper import GeoMapHelper
from geoguessr.client import GeoGuessrClient
from ui.browser_interactor import BrowserInteractor

class GeoAgent:
    def __init__(self, keypoints: dict, llm_wrappers: List[LlmWrapper]):
        self.llm_wrappers = llm_wrappers

        self.image_handler = ImageHandler()
        self.geoguessr_client = GeoGuessrClient()
        self.interactor = UIInteractor(keypoints)
        self.geo_map_helper = GeoMapHelper(keypoints, self.interactor)

    def run(self, rounds_number: int = ROUNDS_NUMBER) -> None:
        browser_interactor = BrowserInteractor()
        self.game_id = browser_interactor.get_game_id()

        game_db_initial = self._save_initial_game_data()

        for round in range(rounds_number):
            sleep(PRE_ROUND_DELAY)
            self._play_round(round + 1)

        self._save_completed_game_data(game_db_initial)

    def _play_round(self, round_number: int) -> None:        
        screenshot = self.interactor.take_image_screenshot()
        screenshot = ImageHandler.preprocess(screenshot)
        screenshot_b64 = ImageHandler.PIL_image_to_base64(screenshot)

        image_path = image_repo.save_image(screenshot, self.game_id, round_number)
        round_db_initial = self._save_initial_round_data(round_number, image_path)

        geolocations = []
        for llm in self.llm_wrappers:
            guess = llm.get_llm_guess([screenshot_b64])
            geolocations.append(guess.geolocation)
            self._save_guess_data(round_db_initial.id, llm.db_id, guess)
        
        aggregated_geolocation = self._aggregate_geolocations(geolocations)

        map_x, map_y = self.geo_map_helper.geolocation_to_map_coordinates(aggregated_geolocation)
        self.interactor.hover_over_map()
        map_x, map_y = self.geo_map_helper.adjust_map_coordinates(map_x, map_y)
        self._submit_guess((map_x, map_y))
        self._save_completed_round_data(round_db_initial)

    def _aggregate_geolocations(self, geolocations: List[Geolocation]) -> Geolocation:
        lat = sum([c.latitude for c in geolocations]) / len(geolocations)
        lng = sum([c.longitude for c in geolocations]) / len(geolocations)
        return Geolocation(lat, lng)

    def _submit_guess(self, position: Tuple[int, int]) -> None:
        self.interactor.click_on_position(*position)
        self.interactor.click_on_confirm()
        self.interactor.move_away_from_map()
        self.interactor.go_to_next_round()

    def _save_guess_data(self, round_id: int, model_id: int, llm_guess: LlmGuess) -> Guess:
        guess = Guess()
        guess.round_id = round_id
        guess.model_id = model_id
        guess.reasoning = llm_guess.reasoning
        guess.seconds_spent = llm_guess.seconds_spent
        guess.predicted_latitude = llm_guess.geolocation.latitude
        guess.predicted_longitude = llm_guess.geolocation.longitude

        guess_db = guess_repo.add_guess(guess)
        return guess_db

    def _save_initial_round_data(self, round_number: int, image_path: str) -> Round:
        game_data = self.geoguessr_client.get_game_data(self.game_id)
        last_round_available = game_data["rounds"][-1]

        round_db = Round()
        round_db.game_token = self.game_id
        round_db.round_number = round_number
        round_db.round_image_url = image_path
        round_db.true_latitude = last_round_available["lat"]
        round_db.true_longitude = last_round_available["lng"]
        round_db.panorama_id = last_round_available["panoId"]
        round_db.country_code = last_round_available["streakLocationCode"]

        round_db_initial = round_repo.add_round(round_db)
        return round_db_initial

    def _save_completed_round_data(self, round_db_initial: Round) -> Round:
        game_data = self.geoguessr_client.get_game_data(self.game_id)
        round_db_initial.round_number = len(game_data["player"]["guesses"])
        last_guess_available = game_data["player"]["guesses"][-1]

        round_db_initial.aggregated_latitude = last_guess_available["lat"]
        round_db_initial.aggregated_longitude = last_guess_available["lng"]
        round_db_initial.score = last_guess_available["roundScoreInPoints"]
        round_db_initial.distance_km = last_guess_available["distanceInMeters"] / 1000

        round_db_final = round_repo.update_round(round_db_initial)
        return round_db_final

    def _save_initial_game_data(self) -> Game:
        game_data = self.geoguessr_client.get_game_data(self.game_id)

        game_db = Game()
        game_db.token = game_data["token"]
        game_db.map = game_data["map"]
        game_db.player_id = game_data["player"]["id"]
        
        game_db_initial = game_repo.add_game_if_not_exists(game_db)
        return game_db_initial

    def _save_completed_game_data(self, game_db_initial: Game) -> Game:
        game_data = self.geoguessr_client.get_game_data(self.game_id)
        
        game_db_initial.rounds_count = game_data["round"]
        game_db_initial.total_score = int(game_data["player"]["totalScore"]["amount"])
        game_db_initial.total_distance_km = game_data["player"]["totalDistanceInMeters"] / 1000

        game_db_final = game_repo.update_game(game_db_initial)
        return game_db_final