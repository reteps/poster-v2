import requests
import json
from image_sources.windows_image import image_open
from io import BytesIO
from image_sources.image_cover_generator import ImageCoverGenerator
from imdb import IMDb

class TMDBCoverGenerator(ImageCoverGenerator):
    def __init__(self, type, api_key, api_url='https://api.themoviedb.org/3', image_url='http://image.tmdb.org/t/p/original', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = api_url
        self.image_url = image_url
        self.type = type
        self.api_key = api_key
        self.imdb = IMDb()
    def _most_popular_movie(self, q):
        if q.isdigit():
            movieid = q
        else:
            movieid = self.imdb.search_movie(q)[0].movieID
        params = {'api_key': self.api_key, 'external_source': 'imdb_id'}
        results = requests.get(self.api_url+'/find/tt'+movieid, params=params).json()
        id, type = None, None
        for kind in results:
            if len(results[kind]) > 0:
                id = results[kind][0]['id']
                type = kind.replace('_results','')
        return id, type
    def _get_images(self, keyword):
        id, type = self._most_popular_movie(keyword)
        params = {'api_key': self.api_key}
        data = requests.get(self.api_url+f'/{type}/{id}/images', params=params).json()
        if self.type == 'all':
            return data['posters'] + data['backdrops']
        return data[self.type]
    def display_data(self):
        pass
    # Override Image Search
    def _search(self, keyword):
        results = self._get_images(keyword)
        # Sort by votes
        return sorted(results, key=lambda x: x['vote_average'])
    # Override Image Processing for a faster return
    def _processed_image(self, img):
        if img['height'] < self.min_height or img['width'] < self.min_width:
            return None
        temp_img = image_open(BytesIO(requests.get(self.image_url + img['file_path']).content))
        return temp_img

if __name__ == '__main__':
    img_maker = TMDBCoverGenerator(
        'backdrops', # posters
        '4237f50f40774d6ed361922c222568a0'
    )
    movie = input()
    cover = img_maker.get_cover(movie, data=False)
    print(cover.size)
    cover.show()
    input('Close > ')
    cover.hide()
    cover.save('file')