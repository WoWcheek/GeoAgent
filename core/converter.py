import math
from numpy import clip
from typing import Tuple

class Converter:
    def __init__(self, keypoints: dict):
        self.map_TL_x, self.map_TL_y = keypoints["map_TL"]
        self.map_w = keypoints["map_BR"][0] - self.map_TL_x
        self.map_h = keypoints["map_BR"][1] - self.map_TL_y

        self.confirm_button_position = keypoints["confirm"]

        self.kodiak_user_x, self.kodiak_user_y = keypoints["kodiak"] 
        self.hobart_user_x, self.hobart_user_y = keypoints["hobart"]
        
        self.kodiak_true_lat, self.kodiak_true_lon = keypoints["kodiak_true"]
        self.hobart_true_lat, self.hobart_true_lon = keypoints["hobart_true"]

    def _geo_lat_to_mercator_y(self, lat: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

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

        x, y = round(x), round(y)

        clipped_map_x = clip(x, self.map_TL_x, self.map_TL_x+self.map_w)
        clipped_map_y = clip(y, self.map_TL_y, self.map_TL_y+self.map_h)

        print(f"Predicted map coordinates: x: {clipped_map_x}, y: {clipped_map_y}")