import os
from requests import Session

GEOGUESSR_API_BASE_URL = "https://www.geoguessr.com/api"

class GeoGuessrClient:
    def __init__(self):
        self.session = Session()
        self.base_url = GEOGUESSR_API_BASE_URL
        self.session.cookies.set("_ncfa", os.environ.get("NCFA_TOKEN"), domain="www.geoguessr.com")
    
    def get_game_data(self, game_token: str):
        url = f"{self.base_url}/v3/games/{game_token}"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching game data: {response.status_code}")