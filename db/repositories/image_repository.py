import os
from io import BytesIO
from PIL.Image import Image
from dotenv import load_dotenv
from config import AZURE_STORAGE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient, ContentSettings

class ImageRepository:
    def __init__(self):
        load_dotenv()
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = AZURE_STORAGE_CONTAINER_NAME
        self.image_settings = ContentSettings(content_type='image/png')

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = blob_service_client.get_container_client(self.container_name)

    def save_image(self, image: Image, game_token: str, round_number: int) -> str:
        image_path = f"{game_token}/{round_number}.png"
        # img_bytes = BytesIO()
        # image.save(img_bytes, format='PNG')
        # img_bytes.seek(0)
        # self.container_client.upload_blob(image_path, img_bytes, content_settings=self.image_settings)
        return f"{self.container_name}:{image_path}"