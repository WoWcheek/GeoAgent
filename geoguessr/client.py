import os
from requests import Session
from config import GEOGUESSR_API_BASE_URL

class GeoGuessrClient:
    def __init__(self):
        self.base_url = GEOGUESSR_API_BASE_URL
        self.session = Session()
        self.session.cookies.set("_ncfa", os.environ.get("NCFA_TOKEN"), domain="www.geoguessr.com")
    
    def get_game_data(self, game_id: str):
        url = f"{self.base_url}/v3/games/{game_id}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching game data: {response.status_code}")