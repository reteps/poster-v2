from image_sources.tmdb_cover_search import TMDBCoverGenerator
from image_sources.google_cover_search import GoogleCoverGenerator
from image_sources.custom_cover_generator import CustomCoverGenerator
from data_sources.movie_source import retrieve_movie_details, modifier
from data_sources.color_source import combo_color_palette, retrieve_user_colors, ext_color_palette
from poster_sources.movie_poster import AlbumStylePoster, ClassicultPoster, ClassicultBarPoster
from image_sources.windows_image import image_open, hide_file
from uploader import create_listing, etsy_instance
import json
from PIL import Image
import random
from pathlib import Path
import argparse

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata, re
    value = unicodedata.normalize('NFKD', value)
    value = str(re.sub('[^\w\s-]', '', value).strip().lower())
    value = str(re.sub('[-\s]+', '-', value))
    # ...
    return value
if __name__ == '__main__':
    split_on_comma = lambda s: [int(item) for item in s.split(',') if len(item) > 0 ]
    parser = argparse.ArgumentParser()
    parser.add_argument('search', type=str, nargs='+', help='Movie / TV Show')
    parser.add_argument('-u', '--url', type=str, help='Custom Image URL')
    parser.add_argument('-g', '--google', type=split_on_comma, help='Google Image Result Numbers')
    parser.add_argument('-i', '--imdb', type=split_on_comma, help='Imdb Image Result Numbers')
    parser.add_argument('-p', '--plot', type=int, help='Plot number')
    args = parser.parse_args()
    print(args)
    query = " ".join(args.search)
    hide_file()
    # '''

    movie_data = modifier(retrieve_movie_details(query), args.plot) # movie
    addl = ''
    if 'tv' in movie_data['rated'].lower():
        addl = ' tv'
    
    if args.url:
        custom_img_maker = CustomCoverGenerator()
        covers = [custom_img_maker.get_cover(args.url, data=False)]
    else:
        tmdb_img_maker = TMDBCoverGenerator('all', '4237f50f40774d6ed361922c222568a0')
        covers = []
        google_img_maker = GoogleCoverGenerator("AIzaSyDC2lWkgbX9OdzNY4OCX8oVoozVTUAkkDc", "f8b95d8f937c12c6a")
        if args.imdb == None or len(args.imdb) > 0:
            covers += tmdb_img_maker.get_covers(movie_data['original_title'], data=False, nums=args.imdb, pause=True)
        if args.google == None or len(args.google) > 0:
            covers += google_img_maker.get_covers(movie_data['original_title'] + addl, data=False,nums=args.google,pause=True)
    nums=None
    e = etsy_instance()
    to_upload = []
    for cover in covers:
        cover_id = f'{random.randint(1,999999999):09d}'
        colors = retrieve_user_colors(cover, combo_color_palette(cover))
        # colors = ext_color_palette(cover)[:5]

        full_data = {
            **movie_data,
            'colors': colors,
            'cover_id': cover_id,
            'title_slug': slugify(movie_data['original_title']) + f"-{movie_data['id']}"
        }
        print(full_data['title_slug'])
        full_data['relative_path'] = f"posters/{full_data['title_slug']}"
        full_data['img_path'] = f"posters/{full_data['title_slug']}/img/{cover_id}.png"
        poster_generator = ClassicultBarPoster(full_data, cover)
        p = poster_generator.get_poster()
        print('Poster created.')
        full_data['img_size'] = p.size
        poster_dir = Path(f"{full_data['relative_path']}/img")
        data_dir = Path(f"{full_data['relative_path']}/data")
        covers_dir = Path(f"{full_data['relative_path']}/covers")
        poster_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        covers_dir.mkdir(parents=True, exist_ok=True)
        p.show()
        upload = 'y' in input('upload > ').strip().lower()
        p.hide()
        print('Saving...')
        p.save(poster_dir / f"{cover_id}.png")
        cover.save(covers_dir / f"{cover_id}.png")
        p.close()
        cover.close()
        with open(data_dir / f"{cover_id}.json", "w") as f:
            json.dump(full_data, f, indent=2)
        if upload:
            print('Poster queued for upload.')
            to_upload.append(full_data)
    for poster_data in to_upload:
        create_listing(e, poster_data)