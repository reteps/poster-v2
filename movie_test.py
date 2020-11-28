from image_sources.tmdb_cover_search import TMDBCoverGenerator
from image_sources.google_cover_search import GoogleCoverGenerator
from data_sources.movie_source import retrieve_movie_details
from data_sources.color_source import combo_color_palette, retrieve_user_colors, ext_color_palette
from poster_sources.movie_poster import AlbumStylePoster, ClassicultPoster
from image_sources.windows_image import image_open, hide_file
import json
from PIL import Image

if __name__ == '__main__':
    img_maker = TMDBCoverGenerator(
        'all',
        '4237f50f40774d6ed361922c222568a0'
    )
    # img_maker = GoogleCoverGenerator(
    #     "AIzaSyDC2lWkgbX9OdzNY4OCX8oVoozVTUAkkDc", "f8b95d8f937c12c6a"
    # )
    # hide_file()
    # '''
    movie = input('series / movie > ')
    # movie = '35 spirited away' # input('series / movie > ')
    num = None
    if movie.split(' ')[0].isdigit():
        num = int(movie.split(' ')[0])
        movie = ' '.join(movie.split(' ')[1:])
    movie_data = retrieve_movie_details(movie, plot=1) # movie
    cover = img_maker.get_cover(movie, data=False, num=num, pause=True)
    colors = retrieve_user_colors(cover, ext_color_palette(cover))
    # colors = ext_color_palette(cover)[:5]
    '''
    movie_data = retrieve_movie_details('alien', plot=2) # movie
    cover = Image.open('temp_image.png')
    colors = [{'color': '131522', 'amount': 1463399}, {'color': '89beb8', 'amount': 928904}, {'color': '4b8c56', 'amount': 555189}, {'color': '002b00', 'amount': 536894}, {'color': '0081a1', 'amount': 74812}]
    # '''
    full_data = {
        **movie_data,
        'colors': colors
    }
    poster_generator = AlbumStylePoster(full_data, cover)
    p = poster_generator.get_poster()
    p.save('file.png')
    p.show()