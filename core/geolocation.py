from typing import Optional

class Geolocation:
    def __init__(self, latitude: Optional[float], longitude: Optional[float]):
        self.latitude = latitude
        self.longitude = longitude
    
    def is_valid(self) -> bool:
        return self.latitude is not None and self.longitude is not None