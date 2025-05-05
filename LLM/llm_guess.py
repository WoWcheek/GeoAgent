from core.geolocation import Geolocation

class LlmGuess:
    def __init__(self, reasoning: str, geolocation: Geolocation, seconds_spent: int, llm_db_id: int = None):
        self.llm_db_id = llm_db_id
        self.reasoning = reasoning
        self.geolocation = geolocation
        self.seconds_spent = seconds_spent