from .image_cover_generator import ImageCoverGenerator
import requests
from .windows_image import image_open
from io import BytesIO
import time
class ItunesCoverGenerator(ImageCoverGenerator):
    def __init__(self, api_key, cx_id, max_size=5000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = max_size

    def display_data(self, i, object):
        print(f"{i+1:02d}|{object['artistName']:20s}|{object['trackCount']:3d}|{object.get('contentAdvisoryRating', 'NONE'):8s}|{object['collectionName']}")
    def _search(self, keyword, limit=6):
        base_data = {'country': 'US', 'media': 'music',
                'entity': 'album', 'limit': limit, 
                'lang': 'en_us'}
        base_data['term'] = keyword
        res = None
        n = 3
        while True:
            res = requests.get('https://itunes.apple.com/search', base_data)
            if res.status_code != 200:
                if n <= 1:
                    raise ValueError('Could not connect to itunes')
                print(f'Error, status code was {res.status_code}, retrying {n} more times...')
                time.sleep(2)
                n -= 1
            else:
                break
        return res.json()['results']
        # Called on every result
    def _processed_image(self, img):
        return image_open(BytesIO(requests.get(img['artworkUrl100'].replace('100x100', f'{self.max_size}x{self.max_size}', 1)).content))
