import base64
from io import BytesIO
from PIL.Image import Image

class ImageHandler:
    def __init__(self, image: Image | None = None):
        self.image = image

    def set_image(self, image: Image) -> None:
        self.image = image

    def convert_to_base64(self) -> str:
        if self.image is None:
            raise ValueError("No image provided")

        buffer = BytesIO()
        self.image.save(buffer, format="PNG")

        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return base64_str