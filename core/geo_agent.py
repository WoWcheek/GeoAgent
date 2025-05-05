from db import *
from LLM import *
from config import *
from time import sleep
from typing import Tuple, List
from LLM import LlmGuess, LlmWrapper
from core.geolocation import Geolocation
from ui.ui_interactor import UIInteractor
from geoguessr.utils import GeoGuessrUtils
from core.geo_processor import GeoProcessor
from core.image_handler import ImageHandler
from core.geo_map_helper import GeoMapHelper
from geoguessr.client import GeoGuessrClient
from ui.browser_interactor import BrowserInteractor

class GeoAgent:
    def __init__(self, keypoints: dict, llm_wrappers: List[LlmWrapper]):
        self.llm_wrappers = llm_wrappers

        self.geo_processor = GeoProcessor()
        self.image_handler = ImageHandler()
        self.geoguessr_client = GeoGuessrClient()
        self.interactor = UIInteractor(keypoints)
        self.geo_map_helper = GeoMapHelper(keypoints, self.interactor)

    def run(self, rounds_number: int = ROUNDS_NUMBER) -> None:
        browser_interactor = BrowserInteractor()
        game_token = browser_interactor.get_game_token()
        self.game = self.save_initial_game_data(game_token)
        self.geoguessr_utils = GeoGuessrUtils(self.game.max_distance_km)

        for _ in range(rounds_number):
            sleep(PRE_ROUND_DELAY)
            game_data_after_round = self.play_round()

        self.game = self.save_completed_game_data(game_data_after_round)

    def play_round(self):        
        screenshot = self.interactor.take_image_screenshot()
        screenshot = ImageHandler.preprocess(screenshot)
        screenshot_b64 = ImageHandler.PIL_image_to_base64(screenshot)

        guesses = [llm.get_llm_guess([screenshot_b64]) for llm in self.llm_wrappers]
        geolocations = [guess.geolocation for guess in guesses]
        aggregated_geolocation = self.geo_processor.aggregate_geolocations(geolocations)

        map_x, map_y = self.geo_map_helper.geolocation_to_map_coordinates(aggregated_geolocation)
        self.interactor.hover_over_map()
        map_x, map_y = self.geo_map_helper.adjust_map_coordinates(map_x, map_y)
        self.submit_guess((map_x, map_y))

        rounds_played = self.game.rounds_count

        while rounds_played == self.game.rounds_count:
            game_data = self.geoguessr_client.get_game_data(self.game.token)
            self.game.rounds_count = len(game_data["player"]["guesses"])

        image_url = image_repo.save_image(screenshot, self.game.token, self.game.rounds_count)
        round_db = self.save_round_data(game_data, image_url)
        true_geolocation = Geolocation(round_db.true_latitude, round_db.true_longitude)

        for guess in guesses:
            self.save_guess_data(round_db.id, guess, true_geolocation)
        
        return game_data

    def submit_guess(self, position: Tuple[int, int]) -> None:
        self.interactor.click_on_position(*position)
        self.interactor.click_on_confirm()
        self.interactor.move_away_from_map()
        self.interactor.go_to_next_round()

    def save_guess_data(self, round_id: int, llm_guess: LlmGuess, true_geolocation: Geolocation) -> Guess:
        guess = Guess()
        guess.round_id = round_id
        guess.model_id = llm_guess.llm_db_id
        guess.latitude = llm_guess.geolocation.latitude
        guess.longitude = llm_guess.geolocation.longitude
        guess.country_code = self.geo_processor.get_country_code(llm_guess.geolocation)
        guess.reasoning = llm_guess.reasoning
        guess.seconds_spent = llm_guess.seconds_spent

        guess.distance_km = self.geo_processor.get_haversine_distance(llm_guess.geolocation, true_geolocation)
        guess.score = self.geoguessr_utils.calculate_score(guess.distance_km)

        return guess_repo.add_guess(guess)

    def save_round_data(self, game_data, image_url: str) -> Round:
        round_number = len(game_data["player"]["guesses"])
        last_round = game_data["rounds"][round_number-1]
        last_guess = game_data["player"]["guesses"][-1]

        round_db = Round()
        round_db.game_token = self.game.token
        round_db.round_number = round_number
        round_db.panorama_id = last_round["panoId"]
        round_db.image_url = image_url
        round_db.true_latitude = last_round["lat"]
        round_db.true_longitude = last_round["lng"]
        round_db.true_country_code = last_round["streakLocationCode"]
        round_db.aggregated_latitude = last_guess["lat"]
        round_db.aggregated_longitude = last_guess["lng"]
        round_db.aggregated_country_code = self.geo_processor.get_country_code(
            Geolocation(round_db.aggregated_latitude, round_db.aggregated_longitude))
        round_db.score = last_guess["roundScoreInPoints"]
        round_db.distance_km = last_guess["distanceInMeters"] / 1000
        round_db = round_repo.add_round(round_db)
        return round_db

    def save_initial_game_data(self, game_token: str) -> Game:
        game_data = self.geoguessr_client.get_game_data(game_token)

        min_bound_lat = game_data["bounds"]["min"]["lat"]
        min_bound_lng = game_data["bounds"]["min"]["lng"]
        min_bound_geolocation = Geolocation(min_bound_lat, min_bound_lng)

        maxbound_lat = game_data["bounds"]["max"]["lat"]
        maxbound_lng = game_data["bounds"]["max"]["lng"]
        max_bound_geolocation = Geolocation(maxbound_lat, maxbound_lng)

        max_distance = self.geo_processor.get_haversine_distance(min_bound_geolocation, max_bound_geolocation)

        game_db = Game()
        game_db.token = game_data["token"]
        game_db.map = game_data["map"]
        game_db.max_distance_km = max_distance
        game_db.player_id = game_data["player"]["id"]
        game_db.rounds_count = len(game_data["player"]["guesses"])
        game_db.start_datetime_utc = GeoGuessrUtils.parse_geoguessr_datetime(
            game_data["rounds"][0]["startTime"])
        
        return game_repo.add_game_if_not_exists(game_db)

    def save_completed_game_data(self, game_data) -> Game:      
        self.game.rounds_count = len(game_data["player"]["guesses"])
        self.game.total_score = int(game_data["player"]["totalScore"]["amount"])
        self.game.total_distance_km = game_data["player"]["totalDistanceInMeters"] / 1000

        return game_repo.update_game(self.game)