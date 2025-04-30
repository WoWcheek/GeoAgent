from config import TEST_RESPONSE_FILE
from core.geolocation import Geolocation

class ResponseMock:
    def __init__(self, geolocation: Geolocation = None):
        with open(TEST_RESPONSE_FILE, "r") as file:
            lines = file.readlines()
        if geolocation is not None:
            lines[-1] = f"Lat: {geolocation.latitude:.4f}, Lng: {geolocation.longitude:.4f}"
        self.content = "".join(lines)