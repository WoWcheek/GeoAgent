import pyautogui
from PIL import Image
from time import sleep
from config import POST_CLICK_DELAY, CLICK_DURATION, POST_ROUND_DELAY

class UIInteractor:
    def __init__(self, keypoints: dict):
        self.image_region = (keypoints["window_TL"][0],
                             keypoints["window_TL"][1],
                             keypoints["window_BR"][0] - keypoints["window_TL"][0],
                             keypoints["window_BR"][1] - keypoints["window_TL"][1])

        self.map_region = (keypoints["point_NW"][0],
                           keypoints["point_NW"][1],
                           keypoints["point_SE"][0] - keypoints["point_NW"][0],
                           keypoints["point_SE"][1] - keypoints["point_NW"][1])
        
        self.position_inside_map = keypoints["point_SE"]
        self.position_outside_map = keypoints["window_BR"]

        self.confirm_button_position = keypoints["confirm"]

    def take_image_screenshot(self) -> Image:
        return pyautogui.screenshot(region=self.image_region)
    
    def take_map_screenshot(self) -> Image:
        return pyautogui.screenshot(region=self.map_region)
    
    @staticmethod
    def move_to_position(x: int, y: int) -> None:
        pyautogui.moveTo(x, y, duration=CLICK_DURATION)
        sleep(POST_CLICK_DELAY)

    def hover_over_map(self) -> None:
        UIInteractor.move_to_position(*self.position_inside_map)

    def move_away_from_map(self) -> None:
        UIInteractor.move_to_position(*self.position_outside_map)

    @staticmethod
    def click_on_position(x: int, y: int) -> None:
        pyautogui.click(x, y, duration=CLICK_DURATION)
        sleep(POST_CLICK_DELAY)
    
    def click_on_confirm(self) -> None:
        UIInteractor.click_on_position(*self.confirm_button_position)

    @staticmethod
    def go_to_next_round() -> None:
        pyautogui.press(" ")
        sleep(POST_ROUND_DELAY)
