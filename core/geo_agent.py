import re
from typing import Tuple  
from config import LLM_RETRY_LIMIT
from core.converter import Converter
from ui.ui_interactor import UIInteractor
from core.image_handler import ImageHandler
from langchain_core.messages import AIMessage
from LLM.prompt_composer import PromptComposer
from langchain_openai import ChatOpenAI as OpenAI
from langchain_anthropic import ChatAnthropic as Anthropic
from langchain_google_genai import ChatGoogleGenerativeAI as Gemini

class GeoAgent:
    def __init__(self, keypoints: dict, LLM_type: OpenAI | Gemini | Anthropic, LLM_name: str):
        self.image_handler = ImageHandler()
        self.prompt_composer = PromptComposer()
        self.interactor = UIInteractor(keypoints)
        self.converter = Converter(keypoints)
        self.LLM: OpenAI | Gemini | Anthropic = LLM_type(model=LLM_name)

    def get_geolocation_from_response(self, llm_response: AIMessage) -> Tuple[float, float]:
        try:
            match = re.search(r"lat:\s*(-?\d+\.\d+),\s*lng:\s*(-?\d+\.\d+)", llm_response.content.lower())
            if match is None: return None
            lat = float(match.group(1))
            lng = float(match.group(2))
            return lat, lng
        except Exception as e:
            print("Error occured while getting geolocation from LLM response: ", e)
            return None
    
    def play_round(self) -> None:        
        screenshot = self.interactor.take_screenshot()
        self.image_handler.set_image(screenshot)
        screenshot_b64 = self.image_handler.convert_to_base64()

        message = self.prompt_composer.compose_prompt([screenshot_b64])

        response = self.LLM.invoke([message])

        geolocation = self.get_geolocation_from_response(response)
        
        retries = 0
        while geolocation is None and retries < LLM_RETRY_LIMIT:
            print(f"Retry {retries + 1} to get a geolocation...")
            response = self.LLM.invoke([message])
            geolocation = self.get_geolocation_from_response(response)
            retries += 1

        if geolocation is None:
            print(f"Can't get a geolocation after {LLM_RETRY_LIMIT} retries.")
            geolocation = [1, 1]
        else:
            print(response.content)
            print(f"Predicted geolocation: lat: {geolocation[0]}, lng: {geolocation[1]}")

        map_x, map_y = self.converter.geolocation_to_mercator_map_pixels(*geolocation)
        print(f"Map coordinates: x: {map_x}, y: {map_y}")
                
        self.interactor.hover_over_map()
        self.interactor.click_on_position(map_x, map_y)
        self.interactor.click_on_confirm()
        self.interactor.move_away_from_map()
        self.interactor.go_to_next_round()
