import pyautogui
from PIL import Image
from ui import move_to_position, click_on_position

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

    def hover_over_map(self) -> None:
        move_to_position(*self.position_inside_map)

    def move_away_from_map(self) -> None:
        move_to_position(*self.position_outside_map)
    
    def click_on_confirm(self) -> None:
        click_on_position(*self.confirm_button_position)
