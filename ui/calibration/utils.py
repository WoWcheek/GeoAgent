from typing import Optional
from config import CALIBRATION_MAP_FILE

def get_base64_calibration_map() -> Optional[str]:
    try:
        with open(CALIBRATION_MAP_FILE) as file:
            return file.read()
    except:
        print("Couldn't found calibration map file.")
        return None