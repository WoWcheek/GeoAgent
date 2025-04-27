import re
from LLM.models import *
from config import LLM_RETRY_LIMIT
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
    def __init__(self, keypoints: dict, LLMs: List[Tuple[OpenAI | Gemini | Anthropic, str]]):
        self.image_handler = ImageHandler()
        self.prompt_composer = PromptComposer()
        self.interactor = UIInteractor(keypoints)
        self.converter = Converter(keypoints, self.interactor)
        self.LLMs = [LLM_type(model=LLM_name) for (LLM_type, LLM_name) in LLMs]

    def get_geolocation_from_response(self, llm_response: AIMessage) -> Optional[Tuple[float, float]]:
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
            geolocation = self.get_geolocation_from_response(response)
            if geolocation:
                coords.append(geolocation)
        if not coords:
            return None
        lat = sum([c[0] for c in coords]) / len(coords)
        lng = sum([c[1] for c in coords]) / len(coords)
        return lat, lng

    def play_round(self) -> None:        
        screenshot = self.interactor.take_image_screenshot()
        self.image_handler.set_image(screenshot)
        self.image_handler.preprocess()
        screenshot_b64 = self.image_handler.convert_to_base64()

        message = self.prompt_composer.compose_prompt([screenshot_b64])

        geolocation = None
        retries = 0
        while geolocation is None and retries <= LLM_RETRY_LIMIT:
            print(f"Attempt {retries + 1} to get geolocation...")
            responses = [llm.invoke([message]) for llm in self.LLMs]
            # responses = [ResponseMock(), ResponseMock((20, 20)), ResponseMock((30, 0))]
            geolocation = self._aggregate_model_geolocations(responses)
            retries += 1

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

        browser_interactor = BrowserInteractor()
        game_id = browser_interactor.get_game_id()
        client = GeoGuessrClient()
        game_data = client.get_game_data(game_id)
        last_guess = game_data["player"]["guesses"][-1]
        print(f"Put geolocation: lat: {last_guess['lat']}, lng: {last_guess['lng']}")