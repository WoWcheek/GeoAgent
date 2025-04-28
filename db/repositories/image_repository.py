import os
from PIL.Image import Image

class ImageRepository:
    def __init__(self):
        self.base_location = "screenshots"
        os.makedirs(self.base_location, exist_ok=True)
    
    def save_image(self, image: Image, game_id: str, round_number: int) -> str:
        game_images_path = os.path.join(self.base_location, game_id)
        os.makedirs(game_images_path, exist_ok=True)
        image_full_path = os.path.join(game_images_path, f"{round_number}.png")
        image.save(image_full_path)
        return image_full_path