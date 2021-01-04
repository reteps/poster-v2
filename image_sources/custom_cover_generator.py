from google_images_search import GoogleImagesSearch
from io import BytesIO
import subprocess
import time
import os
import requests
from image_sources.image_cover_generator import ImageCoverGenerator
from PIL import Image

class CustomCoverGenerator(ImageCoverGenerator):
    def _search(self, url):
        file = requests.get(url).content
        return [file]
    def _processed_image(self, result):
        return Image.open(BytesIO(result))
    def display_data(self):
        pass