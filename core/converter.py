import cv2
import math
from numpy import clip
from typing import Tuple
from ui.calibrator import Calibrator
from ui.ui_interactor import UIInteractor
from core.image_handler import ImageHandler

class Converter:
    def __init__(self, keypoints: dict, ui_interactor: UIInteractor):
        self.ui_interactor = ui_interactor

        self.map_TL_x, self.map_TL_y = keypoints["map_TL"]
        self.map_w = keypoints["map_BR"][0] - self.map_TL_x
        self.map_h = keypoints["map_BR"][1] - self.map_TL_y

        self.kodiak_user_x, self.kodiak_user_y = keypoints["kodiak"] 
        self.hobart_user_x, self.hobart_user_y = keypoints["hobart"]
        
        self.kodiak_true_lat, self.kodiak_true_lon = keypoints["kodiak_true"]
        self.hobart_true_lat, self.hobart_true_lon = keypoints["hobart_true"]

        self.kodiak_true_mercator = self._geo_lat_to_mercator_y(self.kodiak_true_lat)
        self.hobart_true_mercator = self._geo_lat_to_mercator_y(self.hobart_true_lat)

        self.lon_diff_ref = (self.kodiak_true_lon - self.hobart_true_lon)
        self.lat_diff_ref = (self.kodiak_true_mercator - self.hobart_true_mercator)

    def _geo_lat_to_mercator_y(self, lat: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

    def geolocation_to_map_coordinates(self, lat: float, lon: float) -> Tuple[float, float]:
        lon_diff = (self.kodiak_true_lon - lon)
        x = abs(self.kodiak_user_x - self.hobart_user_x) * (lon_diff / self.lon_diff_ref) + self.kodiak_user_x

        mercator_y = self._geo_lat_to_mercator_y(lat)
        lat_diff = (self.kodiak_true_mercator - mercator_y)
        y = abs(self.kodiak_user_y - self.hobart_user_y) * (lat_diff / self.lat_diff_ref) + self.kodiak_user_y

        return x, y
    
    def clip_map_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        clipped_map_x = clip(x, self.map_TL_x, self.map_TL_x+self.map_w)
        clipped_map_y = clip(y, self.map_TL_y, self.map_TL_y+self.map_h)
        return clipped_map_x, clipped_map_y
    
    def adjust_map_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        calibration_map_base64 = Calibrator.get_base64_calibration_map()
        current_map_PIL = self.ui_interactor.take_map_screenshot()

        calibration_map = ImageHandler.base64_to_gray_cv_image(calibration_map_base64)
        current_map = ImageHandler.PIL_to_gray_cv_image(current_map_PIL)

        (shift_x, shift_y), _ = cv2.phaseCorrelate(calibration_map, current_map)
            
        print(f"Detected shift: dx = {shift_x:.2f}, dy = {shift_y:.2f}")

        x += shift_x
        y += shift_y

        return x, y