from core.geolocation import Geolocation

class LlmGuess:
    def __init__(self, reasoning: str, geolocation: Geolocation, seconds_spent: int):
        self.reasoning = reasoning
        self.geolocation = geolocation
        self.seconds_spent = seconds_spent