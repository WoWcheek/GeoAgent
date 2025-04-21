import json
import winsound
import pyautogui
from typing import List, Tuple
from ui.ui_interactor import UIInteractor
from geoguessr.client import GeoGuessrClient
from pynput.keyboard import Key, KeyCode, Listener
from ui.browser_interactor import BrowserInteractor
from config import CALIBRATION_KEY, KEYPOINTS_FILE

class Calibrator:
    def __init__(self, calibration_key: str = CALIBRATION_KEY, keypoints_file: str = KEYPOINTS_FILE):
        self.calibration_key = calibration_key
        self.keypoints_file = keypoints_file
        self.ui_keypoints = {
            "window_TL": "Window top left corner",
            "window_BR": "Window Bottom Right corner",
            "map_TL": "Map top left corner",
            "map_BR": "Map bottom right corner",
            "confirm": "Confirm button",
        }
        self.geo_keypoints = {
            "kodiak": "Kodiak",
            "hobart": "Hobart",
        }
        self.positions = {}
        self.geoguessr_client = GeoGuessrClient()
        self.browser_interactor = BrowserInteractor()

    def _on_press(self, key: Key | KeyCode | None, keypoint: str) -> bool | None:
        if getattr(key, 'char', None) != self.calibration_key: return
        x, y = pyautogui.position()
        winsound.Beep(1000, 500)

        if keypoint in self.ui_keypoints.keys():
            print(f"{self.ui_keypoints[keypoint]} position is ({x}, {y})")
            self.positions[keypoint] = [x, y]
        elif keypoint in self.geo_keypoints.keys():
            print(f"{self.geo_keypoints[keypoint]} position is ({x}, {y})")
            UIInteractor.click_on_position(x, y)
            UIInteractor.click_on_position(*self.positions["confirm"])
            UIInteractor.go_to_next_round()
            self.positions[keypoint] = [x, y]

        return False

    def calibrate_keypoints(self) -> dict:
        self._calibrate_user_keypoints()

        game_id = self.browser_interactor.get_game_id()
        self._calibrate_true_geo_keypoints(game_id)

        with open(self.keypoints_file, "w") as f:
            json.dump(self.positions, f, indent=2)

        return self.positions

    def _calibrate_user_keypoints(self) -> dict:
        for keypoint in [*self.ui_keypoints.keys(), *self.geo_keypoints.keys()]:
            human_readable_keypoint = self.ui_keypoints.get(keypoint, self.geo_keypoints.get(keypoint))
            print(f"Place cursor at {human_readable_keypoint} and press key '{self.calibration_key}'")
            with Listener(on_press=lambda key: self._on_press(key, keypoint)) as listener:
                listener.join(30)

        return self.positions

    def _calibrate_true_geo_keypoints(self, game_id: str | None) -> dict:
        try:
            calibration_game_data = self.geoguessr_client.get_game_data(game_id)
            calibration_guesses = calibration_game_data["player"]["guesses"][:2]
            (kodiak_coords, hobart_coords) = (calibration_guesses[0]["lat"], calibration_guesses[0]["lng"]),\
                                             (calibration_guesses[1]["lat"], calibration_guesses[1]["lng"])
        except:
            # These are the default coordinates for Kodiak, Alaska and Hobart, Tasmania
            (kodiak_coords, hobart_coords) = (57.7916, -152.4083), (-42.8833, 147.3355)
        
        self.positions["kodiak_true"] = kodiak_coords
        self.positions["hobart_true"] = hobart_coords

        return self.positions