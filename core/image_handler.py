from PIL.Image import Image, Resampling
from PIL.ImageEnhance import Contrast, Sharpness

class ImageHandler:
    def __init__(self, crop_fraction: float = 0.8, processed_image_size: tuple = (512, 512)):
        self.processed_image_size = processed_image_size
        self.crop_fraction = crop_fraction
        self.contrast_factor = 1.1
        self.sharpness_factor = 1.3

    def preprocess(self, image: Image) -> Image:
        img = image.convert("RGB")

        width, height = img.size
        new_width = int(width * self.crop_fraction)
        new_height = int(height * self.crop_fraction)

        left = (width - new_width) // 2
        top = (height - new_height) // 2

        img = img.crop((left, top, left + new_width, top + new_height))
        img = img.resize(self.processed_image_size, Resampling.LANCZOS)
        
        img = Contrast(img).enhance(self.contrast_factor)
        img = Sharpness(img).enhance(self.sharpness_factor)

        return img
    