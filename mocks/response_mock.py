from typing import Tuple
from config import TEST_RESPONSE_FILE

class ResponseMock:
    def __init__(self, coords: Tuple[float, float] = None):
        with open(TEST_RESPONSE_FILE, "r") as file:
            lines = file.readlines()
        if coords is not None:
            lines[-1] = f"Lat: {coords[0]:.4f}, Lng: {coords[1]:.4f}"
        self.content = "".join(lines)