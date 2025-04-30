import cv2
import math
from numpy import clip
from typing import Tuple
from ui.calibrator import Calibrator
from core.geolocation import Geolocation
from ui.ui_interactor import UIInteractor
from core.image_handler import ImageHandler

class GeoMapHelper:
    def __init__(self, keypoints: dict, ui_interactor: UIInteractor):
        self.ui_interactor = ui_interactor

        self.point_NW_user_x, self.point_NW_user_y = keypoints["point_NW"] 
        self.point_SE_user_x, self.point_SE_user_y = keypoints["point_SE"]
        
        self.point_NW_true_lat, self.point_NW_true_lon = keypoints["point_NW_true"]
        self.point_SE_true_lat, self.point_SE_true_lon = keypoints["point_SE_true"]

        self.point_NW_true_mercator = self._geo_lat_to_mercator_y(self.point_NW_true_lat)
        self.point_SE_true_mercator = self._geo_lat_to_mercator_y(self.point_SE_true_lat)

        self.lon_diff_ref = (self.point_NW_true_lon - self.point_SE_true_lon)
        self.lat_diff_ref = (self.point_NW_true_mercator - self.point_SE_true_mercator)

    def _geo_lat_to_mercator_y(self, lat: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

    def geolocation_to_map_coordinates(self, geolocation: Geolocation) -> Tuple[float, float]:
        lon_diff = (self.point_NW_true_lon - geolocation.longitude)
        x = abs(self.point_NW_user_x - self.point_SE_user_x) * (lon_diff / self.lon_diff_ref) + self.point_NW_user_x

        mercator_y = self._geo_lat_to_mercator_y(geolocation.latitude)
        lat_diff = (self.point_NW_true_mercator - mercator_y)
        y = abs(self.point_NW_user_y - self.point_SE_user_y) * (lat_diff / self.lat_diff_ref) + self.point_NW_user_y

        return x, y
    
    def clip_map_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        clipped_map_x = clip(x, self.point_NW_user_x, self.point_SE_user_x)
        clipped_map_y = clip(y, self.point_NW_user_y, self.point_SE_user_y)
        return clipped_map_x, clipped_map_y
    
    def adjust_map_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        calibration_map_base64 = Calibrator.get_base64_calibration_map()
        current_map_PIL = self.ui_interactor.take_map_screenshot()

        calibration_map = ImageHandler.base64_to_gray_cv_image(calibration_map_base64)
        current_map = ImageHandler.PIL_to_gray_cv_image(current_map_PIL)

        (shift_x, shift_y), _ = cv2.phaseCorrelate(calibration_map, current_map)

        x += shift_x
        y += shift_y

        x_clipped, y_clipped = self.clip_map_coordinates(x, y)

        return x_clipped, y_clipped