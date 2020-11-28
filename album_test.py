from image_sources.itunes_cover_generator import ItunesCoverGenerator
from data_sources.music_source import retrieve_spotify_data, string_mod
from data_sources.color_source import ext_color_palette, retrieve_user_colors
from poster_sources.music_poster import MusicPoster
from image_sources.windows_image import image_open
import json


if __name__ == '__main__':
    '''
    img_maker = ItunesCoverGenerator(
        'backdrops', # posters
        '4237f50f40774d6ed361922c222568a0'
    )
    album = input('ALBUM > ')
    cover, object = img_maker.get_cover(album, pause=False)
    color_data = {
        'colors': colors
    }
    itunes_data = {
        'id': object['collectionId'],
        'itunes_artist': string_mod(object["artistName"], secondary_option=0),
        'itunes_album': string_mod(object["collectionName"], secondary_option=0)
    }

    specific_movie = f'{itunes_data["itunes_artist"]} {itunes_data["itunes_album"]}'
    spotify_data = retrieve_spotify_data(specific_movie)
    full_data = {
        **itunes_data, **spotify_data, **color_data
    }
    '''
    with open('test_data.json', 'r') as f:
        full_data = json.load(f)
        cover = image_open('file.png')
        colors = retrieve_user_colors(cover, ext_color_palette(cover))
        full_data['colors'] = colors
        poster_generator = MusicPoster(full_data, cover)
        p = poster_generator.get_poster()
        p.show()
