import math
from numpy import clip
from typing import Tuple

class Converter:
    def __init__(self, keypoints: dict):
        self.map_TL_x, self.map_TL_y = keypoints["map_TL"]
        self.map_w = keypoints["map_BR"][0] - self.map_TL_x
        self.map_h = keypoints["map_BR"][1] - self.map_TL_y

        self.confirm_button_position = keypoints["confirm"]

        self.kodiak_x, self.kodiak_y = keypoints["kodiak"]
        self.hobart_x, self.hobart_y = keypoints["hobart"]

        self.kodiak_lat, self.kodiak_lon = keypoints["kodiak_true"]
        self.hobart_lat, self.hobart_lon = keypoints["hobart_true"]

        self._init_scaling()

    def _geo_lat_to_mercator_y(self, lat: float) -> float:
        return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

    def _init_scaling(self):
        self.lon_range = self.kodiak_lon - self.hobart_lon
        self.lat_range = self._geo_lat_to_mercator_y(self.kodiak_lat) - self._geo_lat_to_mercator_y(self.hobart_lat)

        self.pixel_dx = self.kodiak_x - self.hobart_x
        self.pixel_dy = self.kodiak_y - self.hobart_y

    def geolocation_to_mercator_map_pixels(self, lat: float, lng: float) -> Tuple[int, int]:
        x_ratio = ((self.kodiak_lon - lng) / self.lon_range) if self.lon_range != 0 else 0.0
        x = self.kodiak_x - self.pixel_dx * x_ratio

        mercator_lat = self._geo_lat_to_mercator_y(lat)
        mercator_ref = self._geo_lat_to_mercator_y(self.kodiak_lat)

        y_ratio = ((mercator_ref - mercator_lat) / self.lat_range) if self.lat_range != 0 else 0.0
        y = self.kodiak_y - self.pixel_dy * y_ratio

        clipped_x = int(clip(round(x), self.map_TL_x, self.map_TL_x + self.map_w))
        clipped_y = int(clip(round(y), self.map_TL_y, self.map_TL_y + self.map_h))

        return clipped_x, clipped_y