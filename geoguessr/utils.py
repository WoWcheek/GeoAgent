from math import exp
from datetime import datetime, timezone

def calculate_geoguessr_score(distance_km: float, max_distance_km: float) -> int:
    score = 5000 * exp(-10 * distance_km / max_distance_km)
    return int(score)
    
def parse_geoguessr_datetime(dt_str: str) -> datetime:
    if '.' in dt_str:
        dt_str = dt_str.split('.')[0] + dt_str[dt_str.find('+'):]
    dt = datetime.fromisoformat(dt_str)
    return dt.astimezone(timezone.utc).replace(tzinfo=None, microsecond=0)