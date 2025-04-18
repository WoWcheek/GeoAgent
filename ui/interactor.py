import pyautogui
from PIL import Image
from time import sleep
from config import POST_CLICK_DELAY_IN_SECONDS, CLICK_DURATION_IN_SECONDS, POST_ROUND_DELAY_IN_SECONDS

class Interactor:
    def __init__(self, keypoints: dict):
        self.screenshot_region = (keypoints["window_TL"][0],
                                  keypoints["window_TL"][1],
                                  keypoints["window_BR"][0] - keypoints["window_TL"][0],
                                  keypoints["window_BR"][1] - keypoints["window_TL"][1])
        
        self.map_TL_x, self.map_TL_y = keypoints[f"map_TL"]
        self.map_w = keypoints["map_BR"][0] - self.map_TL_x
        self.map_h = keypoints["map_BR"][1] - self.map_TL_y

        self.confirm_button_position = keypoints["confirm"]

    def take_screenshot(self) -> Image:
        return pyautogui.screenshot(region=self.screenshot_region)
    
    def move_to_position(self, x: int, y: int) -> None:
        pyautogui.moveTo(x, y, duration=CLICK_DURATION_IN_SECONDS)
        sleep(POST_CLICK_DELAY_IN_SECONDS)

    def hover_over_map(self) -> None:
        map_bottom_right_position = (self.map_TL_x + self.map_w - 10, self.map_TL_y + self.map_h - 10)
        self.move_to_position(*map_bottom_right_position)

    def move_away_from_map(self) -> None:
        position_outside_of_map = (self.map_TL_x + self.map_w + 10, self.map_TL_y + self.map_h + 10)
        self.move_to_position(*position_outside_of_map)

    def click_on_position(self, x: int, y: int) -> None:
        pyautogui.click(x, y, duration=CLICK_DURATION_IN_SECONDS)
        sleep(POST_CLICK_DELAY_IN_SECONDS)
    
    def click_on_confirm(self) -> None:
        self.click_on_position(*self.confirm_button_position)

    def go_to_next_round(self) -> None:
        pyautogui.press(" ")
        sleep(POST_ROUND_DELAY_IN_SECONDS)