from typing import List
from config import PROMPT_FILE
from langchain_core.messages import HumanMessage

class PromptComposer:
    def __init__(self, prompt_file_path: str = PROMPT_FILE):
        with open(prompt_file_path, "r") as f:
            self.text_instructions = f.read()

    def compose_prompt(self, images_base64: List[str]) -> HumanMessage:
        content = [{"type": "text", "text": self.text_instructions}]

        for img in images_base64:
            content += [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}]

        return HumanMessage(content=content)
