from config import TEST_RESPONSE_FILE

class ResponseMock:
    def __init__(self):
        with open(TEST_RESPONSE_FILE, "r") as file:
            self.content = file.read()