import json
import pyautogui
from config import CALIBRATION_KEY, KEYPOINTS_FILE_PATH
from pynput.keyboard import Key, KeyCode, Listener

class Calibrator:
    def __init__(self, calibration_key: str = CALIBRATION_KEY, keypoints_file: str = KEYPOINTS_FILE_PATH):
        self.calibration_key = calibration_key
        self.keypoints_file = keypoints_file
        self.keypoints = {
            "window_TL": "Window top left corner",
            "window_BR": "Window Bottom Right corner",
            "map_TL": "Map top left corner",
            "map_BR": "Map bottom right corner",
            "confirm": "Confirm button",
            "kodiak": "Kodiak",
            "hobart": "Hobart",
        }
        self.positions = {}

    def _on_press(self, key: Key | KeyCode | None, keypoint: str) -> bool | None:
        if getattr(key, 'char', None) != self.calibration_key:
            return
        x, y = pyautogui.position()
        print(f"{self.keypoints[keypoint]} position is ({x}, {y})")
        self.positions[keypoint] = [x, y]
        return False

    def calibrate_user_keypoints(self) -> dict:
        for keypoint in self.keypoints.keys():
            print(f"Place cursor at {self.keypoints[keypoint]} and press key '{self.calibration_key}'")
            with Listener(on_press=lambda key: self._on_press(key, keypoint)) as listener:
                listener.join(30)
        with open(self.keypoints_file, "w") as f:
            json.dump(self.positions, f, indent=2)
        return self.positions