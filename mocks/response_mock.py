from config import TEST_RESPONSE_FILE_PATH

class ResponseMock:
    def __init__(self):
        with open(TEST_RESPONSE_FILE_PATH, "r") as file:
            self.content = file.read()