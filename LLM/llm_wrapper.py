import re
from time import time
from typing import List
from LLM import LlmGuess, LLM_type
from config import LLM_RETRY_LIMIT
from core.geolocation import Geolocation
from langchain_core.messages import HumanMessage
from db import Vendor, Model, vendor_repo, model_repo

class LlmWrapper:
    def __init__(self, model_type: LLM_type, model_name: str, prompt_file_path: str):
        self.model = model_type(model=model_name)

        self.db_id = self.get_db_model_id(model_type, model_name)

        with open(prompt_file_path, "r") as f:
            self.text_instructions = f.read()
    
    def get_db_model_id(self, model_type: LLM_type, model_name: str) -> int:
        vendor = Vendor()
        vendor.name = model_type.__name__
        vendor_db = vendor_repo.add_vendor_if_not_exists(vendor)

        model = Model()
        model.vendor_id = vendor_db.id
        model.model_name = model_name
        model_db = model_repo.add_model_if_not_exists(model)
        
        return model_db.id

    def compose_prompt(self, images_base64: List[str]) -> HumanMessage:
        content = [{"type": "text", "text": self.text_instructions}]

        for img in images_base64:
            content += [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}]

        return HumanMessage(content=content)

    def extract_geolocation_from_llm_response(self, llm_response: str) -> Geolocation:
        try:
            match = re.search(r"lat:\s*(-?\d+\.\d+),\s*lng:\s*(-?\d+\.\d+)", llm_response.lower().replace("*", ""))
            if match is None: raise Exception("Geolocation is not provided or does not match required format.")
            lat = float(match.group(1))
            lng = float(match.group(2))
            return Geolocation(lat, lng)
        except Exception as e:
            print("Error while parsing LLM response:", e, llm_response, sep="\n")
            return Geolocation(None, None)
    
    def get_llm_guess(self, images_base64: List[str]) -> LlmGuess:
        geolocation = Geolocation(None, None)
        retries = 0
        request_start_time = time()
        while not geolocation.is_valid() and retries <= LLM_RETRY_LIMIT:
            message = self.compose_prompt(images_base64)
            response = self.model.invoke([message])
            geolocation = self.extract_geolocation_from_llm_response(response.content)
            retries += 1
        request_end_time = time()
        seconds_spent = int(request_end_time - request_start_time)
        return LlmGuess(response.content, geolocation, seconds_spent, self.db_id)