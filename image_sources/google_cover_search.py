from google_images_search import GoogleImagesSearch
from io import BytesIO
import subprocess
import time
import os
from image_sources.image_cover_generator import ImageCoverGenerator


class GoogleCoverGenerator(ImageCoverGenerator):
    def __init__(self, api_key, cx_id, params={"num": 50, "imgSize": "HUGE"}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gis = GoogleImagesSearch(api_key, cx_id, validate_images=True)
        self.params = params

    def _search(self, keyword):
        self.params["q"] = keyword
        self.gis.search(self.params)
        return self.gis.results()
    def display_data(self):
        pass

if __name__ == "__main__":
    img_maker = GoogleCoverGenerator(
        "AIzaSyDC2lWkgbX9OdzNY4OCX8oVoozVTUAkkDc", "f8b95d8f937c12c6a"
    )
    movie = input()
    cover,_ = img_maker.get_cover(movie)
    print(cover.size)
    cover.show()