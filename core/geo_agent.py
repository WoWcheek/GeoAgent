import re
import math
from numpy import clip
from typing import Tuple  
from config import LLM_RETRY_LIMIT
from ui.interactor import Interactor
from core.image_handler import ImageHandler
from LLM.prompt_composer import PromptComposer
from langchain_core.messages import BaseMessage

class GeoAgent:
    def __init__(self, user_keypoints, LLM_type, LLM_name):
        self.image_handler = ImageHandler()
        self.prompt_composer = PromptComposer()
        self.interactor = Interactor(user_keypoints)

        self.LLM = LLM_type(model=LLM_name)

        self._initialize_true_keypoints()
        self._initialize_user_keypoints(user_keypoints)

    def _initialize_user_keypoints(self, keypoints: dict) -> None:
        self.map_TL_x, self.map_TL_y = keypoints["map_TL"]
        self.map_w = keypoints["map_BR"][0] - self.map_TL_x
        self.map_h = keypoints["map_BR"][1] - self.map_TL_y

        self.confirm_button_position = keypoints["confirm"]

        self.kodiak_user_x, self.kodiak_user_y = keypoints["kodiak"] 
        self.hobart_user_x, self.hobart_user_y = keypoints["hobart"]   

    def _initialize_true_keypoints(self) -> None:
        self.kodiak_true_lat, self.kodiak_true_lon = (57.7916, -152.4083)
        self.hobart_true_lat, self.hobart_true_lon = (-42.8833, 147.3355)

    def _geo_lat_to_mercator_y(self, lat: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

    def get_geolocation_from_llm_response(self, llm_response: BaseMessage) -> Tuple[float, float]:
        try:
            match = re.search(r"lat:\s*(-?\d+\.\d+),\s*lon:\s*(-?\d+\.\d+)", llm_response.content.lower())

            if match is None:
                return [1, 1]
            
            lat = float(match.group(1))
            lon = float(match.group(2))
            print(f"Predicted geolocation: lat: {lat}, lon: {lon}")

            map_x, map_y = self.geolocation_to_mercator_map_pixels(lat, lon)

            clipped_map_x = clip(map_x, self.map_TL_x, self.map_TL_x+self.map_w)
            clipped_map_y = clip(map_y, self.map_TL_y, self.map_TL_y+self.map_h)

            print(f"Predicted map coordinates: x: {clipped_map_x}, y: {clipped_map_y}")

            return clipped_map_x, clipped_map_y
        except Exception as e:
            print("Error occured while getting map coordinates from LLM response: ", e)
            return None
    
    def geolocation_to_mercator_map_pixels(self, lat: float, lon: float) -> Tuple[int, int]:
        lon_diff_ref = (self.kodiak_true_lon - self.hobart_true_lon)
        lon_diff = (self.kodiak_true_lon - lon)

        x = abs(self.kodiak_user_x - self.hobart_user_x) * (lon_diff / lon_diff_ref) + self.kodiak_user_x

        mercator_y1 = self._geo_lat_to_mercator_y(self.kodiak_true_lat)
        mercator_y2 = self._geo_lat_to_mercator_y(self.hobart_true_lat)
        mercator_y = self._geo_lat_to_mercator_y(lat)

        lat_diff_ref = (mercator_y1 - mercator_y2)
        lat_diff = (mercator_y1 - mercator_y)

        y = abs(self.kodiak_user_y - self.hobart_user_y) * (lat_diff / lat_diff_ref) + self.kodiak_user_y

        return round(x), round(y)
    
    def play_round(self):        
        screenshot = self.interactor.take_screenshot()
        self.image_handler.set_image(screenshot)
        screenshot_b64 = self.image_handler.convert_to_base64()

        message = self.prompt_composer.compose_prompt([screenshot_b64])

        response = self.LLM.invoke([message])
        location = self.get_geolocation_from_llm_response(response)
        
        retries = 0
        while location is None and retries < LLM_RETRY_LIMIT:
            print(f"Retry {retries + 1} to get a location...")
            response = self.LLM.invoke([message])
            location = self.get_geolocation_from_llm_response(response)
            retries += 1
        
        print(response.content)

        if location is None:
            print(f"Can't get a location after {LLM_RETRY_LIMIT} retries.")
            location = [1, 1]
        
        self.interactor.hover_over_map()
        self.interactor.click_on_position(*location)
        self.interactor.click_on_confirm()
        self.interactor.move_away_from_map()
        self.interactor.go_to_next_round()
