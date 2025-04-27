import json
import winsound
import pyautogui
from typing import Optional
from ui.ui_interactor import UIInteractor
from core.image_handler import ImageHandler
from geoguessr.client import GeoGuessrClient
from pynput.keyboard import Key, KeyCode, Listener
from ui.browser_interactor import BrowserInteractor
from config import CALIBRATION_KEY, KEYPOINTS_FILE, CALIBRATION_MAP_FILE

class Calibrator:
    def __init__(self):
        self.ui_keypoints = {
            "window_TL": "Window top left corner",
            "window_BR": "Window Bottom Right corner",
            "confirm": "Confirm button",
        }
        self.geo_keypoints = {
            "point_NW": "North West point on map",
            "point_SE": "South East point on map",
        }
        self.positions = {}
        self.geoguessr_client = GeoGuessrClient()
        self.browser_interactor = BrowserInteractor()

    def _on_press_ui_keypoints(self, key: Optional[Key | KeyCode], keypoint: str):
        if getattr(key, 'char', None) != CALIBRATION_KEY: return

        x, y = pyautogui.position()
        winsound.Beep(1000, 500)

        print(f"{self.ui_keypoints[keypoint]} position is ({x}, {y})")
        self.positions[keypoint] = [x, y]

        return False
    
    def _on_press_geo_keypoints(self, key: Optional[Key | KeyCode], keypoint: str):
        if getattr(key, 'char', None) != CALIBRATION_KEY: return
        
        x, y = pyautogui.position()
        winsound.Beep(1000, 500)

        print(f"{self.geo_keypoints[keypoint]} position is ({x}, {y})")

        UIInteractor.click_on_position(x, y)
        UIInteractor.click_on_position(*self.positions["confirm"])
        UIInteractor.move_to_position(*self.positions["window_BR"])
        UIInteractor.go_to_next_round()

        self.positions[keypoint] = [x, y]
        self._calibrate_true_geo_keypoint(keypoint)

        return False

    def calibrate_keypoints(self) -> dict:
        self._calibrate_ui_keypoints()
        self.game_id = self.browser_interactor.get_game_id()
        self._calibrate_geo_keypoints()

        calibration_map_image = self._capture_calibration_map()
        calibration_map_base64 = ImageHandler.PIL_image_to_base64(calibration_map_image)

        with open(CALIBRATION_MAP_FILE, "w") as file:
            file.write(calibration_map_base64)

        with open(KEYPOINTS_FILE, "w") as file:
            json.dump(self.positions, file)

        return self.positions

    def _calibrate_ui_keypoints(self) -> dict:
        for keypoint, human_readable_keypoint in self.ui_keypoints.items():
            print(f"Place cursor at {human_readable_keypoint} and press key '{CALIBRATION_KEY}'")
            with Listener(on_press=lambda key: self._on_press_ui_keypoints(key, keypoint)) as listener:
                listener.join(30)

        return self.positions
    
    def _calibrate_geo_keypoints(self) -> dict:
        for keypoint, human_readable_keypoint in self.geo_keypoints.items():
            print(f"Place cursor at {human_readable_keypoint} and press key '{CALIBRATION_KEY}'")
            with Listener(on_press=lambda key: self._on_press_geo_keypoints(key, keypoint)) as listener:
                listener.join(30)

        return self.positions

    def _calibrate_true_geo_keypoint(self, keypoint: str) -> dict:
        calibration_game_data = self.geoguessr_client.get_game_data(self.game_id)
        last_calibration_guess = calibration_game_data["player"]["guesses"][-1]
        geo_coords = (last_calibration_guess["lat"], last_calibration_guess["lng"])
        print(f"True geolocation of {self.geo_keypoints[keypoint]} is {geo_coords}")      
        self.positions[keypoint+"_true"] = geo_coords
        return self.positions
    
    def _capture_calibration_map(self):
        ui_interactor = UIInteractor(self.positions)
        ui_interactor.click_on_confirm()
        return ui_interactor.take_map_screenshot()

    @staticmethod
    def get_base64_calibration_map() -> Optional[str]:
        try:
            with open(CALIBRATION_MAP_FILE) as file:
                calibration_map_base64_image = file.read()
        except:
            print("Couldn't found calibration map file.")
            calibration_map_base64_image = None
        return calibration_map_base64_image