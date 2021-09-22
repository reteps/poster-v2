from image_sources.tmdb_cover_search import TMDBCoverGenerator
from image_sources.google_cover_search import GoogleCoverGenerator
from image_sources.custom_cover_generator import CustomCoverGenerator
from image_sources.itunes_cover_generator import ItunesCoverGenerator
from data_sources.movie_source import retrieve_movie_details, modifier
from data_sources.color_source import (
    combo_color_palette,
    retrieve_user_colors,
    ext_color_palette,
)
from poster_sources.movie_poster import TheFilmPlanet, Classicult, PeliculaPrint
from poster_sources.music_poster import AlbumArtEngineer
from data_sources.music_source import retrieve_spotify_data
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
    import unicodedata
    import re

    value = unicodedata.normalize("NFKD", value)
    value = str(re.sub("[^\w\s-]", "", value).strip().lower())
    value = str(re.sub("[-\s]+", "-", value))
    # ...
    return value


if __name__ == "__main__":
    # Parse arguments
    def split_on_comma(s): return [int(item)
                                   for item in s.split(",") if len(item) > 0]
    choices = ["movie", "music"]
    parser = argparse.ArgumentParser()
    parser.add_argument("search", type=str, nargs="+",
                        help="Movie / TV Show / Album")
    parser.add_argument(
        "-t", "--type", choices=choices, required=True, help="Music/Movie Poster"
    )
    parser.add_argument("-u", "--url", type=str, help="Custom Image URL")
    parser.add_argument(
        "-g",
        "--google",
        nargs="?",
        const=[],
        type=split_on_comma,
        help="Google Image Result Numbers",
    )
    parser.add_argument(
        "-m",
        "--movie",
        nargs="?",
        const=[],
        type=split_on_comma,
        help="Imdb Image Result Numbers",
    )
    parser.add_argument(
        "-i",
        "--itunes",
        nargs="?",
        const=[],
        type=split_on_comma,
        help="Itunes Image Result Numbers",
    )
    parser.add_argument("-a", "--album", type=int, help="Album number")
    parser.add_argument("-p", "--plot", type=int, help="Plot number")
    parser.add_argument("-f", "--fast", help="Fast colors",
                        action="store_true")
    args = parser.parse_args()
    print(args)
    query = " ".join(args.search)
    hide_file()

    # Get Data & Poster Type & Title Slugs
    data = None
    Poster = None
    title_slug = None
    search = None
    if args.type == "movie":
        Poster = PeliculaPrint  # TheFilmPlanet
        data = modifier(retrieve_movie_details(query), args.plot)  # movie
        title_slug = slugify(data["original_title"]) + f"-{data['id']}"
        search = data["original_title"]
    elif args.type == "music":
        Poster = AlbumArtEngineer
        data = retrieve_spotify_data(query, args.album)
        title_slug = slugify(data["title"]) + f"-{data['release_date']}"
        search = data["title"] + " " + data["artist"]
    # Get Covers
    covers = []
    if args.url:
        custom_img_maker = CustomCoverGenerator()
        covers += [custom_img_maker.get_cover(args.url, data=False)]
    if isinstance(args.movie, list):
        tmdb_img_maker = TMDBCoverGenerator(
            "all", "4237f50f40774d6ed361922c222568a0")
        covers += tmdb_img_maker.get_covers(
            search, data=False, nums=args.movie, pause=True
        )
    if isinstance(args.itunes, list):
        img_maker = ItunesCoverGenerator(
            "backdrops", "4237f50f40774d6ed361922c222568a0"  # posters
        )
        covers += img_maker.get_covers(search,
                                       pause=False, nums=args.album, data=False)
    if isinstance(args.google, list):
        google_img_maker = GoogleCoverGenerator(
            "AIzaSyDC2lWkgbX9OdzNY4OCX8oVoozVTUAkkDc", "f8b95d8f937c12c6a"
        )
        covers += google_img_maker.get_covers(
            search, data=False, nums=args.google, pause=True
        )

    if len(covers) == 0:
        raise ValueError("Please specify 1 or more cover engines")
    nums = None
    e = etsy_instance()
    to_upload = []
    for cover in covers:
        cover_id = f"{random.randint(1,999999999):09d}"
        if args.fast:
            colors = ext_color_palette(cover)[:5]
        else:
            colors = retrieve_user_colors(cover, combo_color_palette(cover))

        full_data = {
            **data,
            "colors": colors,
            "cover_id": cover_id,
            "title_slug": title_slug,
        }
        full_data["relative_path"] = f"posters/{full_data['title_slug']}"
        full_data["img_path"] = f"posters/{full_data['title_slug']}/img/{cover_id}.png"
        p = Poster(full_data, cover).get_poster()
        print(f"{full_data['title_slug']}/img/{cover_id} Created.")
        full_data["img_size"] = p.size
        poster_dir = Path(f"{full_data['relative_path']}/img")
        data_dir = Path(f"{full_data['relative_path']}/data")
        covers_dir = Path(f"{full_data['relative_path']}/covers")
        poster_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        covers_dir.mkdir(parents=True, exist_ok=True)
        p.show()
        upload = "y" in input("upload > ").strip().lower()
        p.hide()
        print("Saving...")
        p.save(poster_dir / f"{cover_id}.png")
        cover.save(covers_dir / f"{cover_id}.png")
        p.close()
        cover.close()
        with open(data_dir / f"{cover_id}.json", "w") as f:
            json.dump(full_data, f, indent=2)
        if upload:
            print("Poster queued for upload.")
            to_upload.append(full_data)
    for poster_data in to_upload:
        create_listing(e, poster_data)
