# poster-v2
A movie and music poster generator engine written in python for some reason.


![ex_1.png](ex_1.png)
![ex_2.png](ex_2.png)

## How it works

`create_poster.py` is a CLI tool that: fetches movie metadata (title, plot,
cast, runtime, director, etc.), lets you interactively review/edit those
details, downloads a cover image from a chosen source, extracts a color
palette from that image, and renders a styled poster PNG. Note: IMDb blocks
scraping now, so movie metadata is fetched from the **TMDB API** instead
(see `data_sources/movie_source.py` and `image_sources/tmdb_cover_search.py`).

### One-time setup

```bash
python3.11 -m venv .venv   # Python 3.11 recommended; some deps break on 3.14
source .venv/bin/activate
pip install Pillow imdbpy dateparser colorthief requests python-dotenv \
            spotipy google-images-search tqdm requests_oauthlib extcolors
```

You also need a `fonts/` folder (gitignored, not included in the repo) with:
- `fonts/Gidole-Regular.ttf`
- `fonts/Sequel/Sequel100Black-85.ttf` (a heavy black sans; e.g. Montserrat-Black works as a substitute)
- `fonts/Aku&Kamu.otf` (only needed for music posters)

### Generating a movie poster

```bash
source .venv/bin/activate
python create_poster.py "Movie Title" -t movie -m 1 -f
```

- `-t movie` selects the movie poster path.
- `-m 1` picks TMDB cover-image result #1 directly. You can also pass
  `-m` with no number to browse a contact-sheet grid of every candidate
  image, but that requires an interactive image viewer and a Windows-only
  font, so picking an index directly (`-m 1`, `-m 2`, ...) is easier on
  macOS/Linux.
- `-f` (fast) skips interactive color-palette picking.
- `-u URL` lets you supply your own custom cover image instead.
- `-g`/`-i` use Google Images / iTunes as the cover source instead of TMDB.

During the run you'll be prompted to:
1. Review/edit metadata (title, plot, director, writers, etc.) — press
   Enter to accept the defaults shown, or type a field number to edit it.
2. Preview the rendered poster, then answer `upload >` — type `n` (or
   just press Enter) to skip Etsy upload and keep the poster local.

The poster is saved to `posters/<title-slug>-<tmdb-id>/img/<cover-id>.png`,
with the raw cover image and metadata JSON saved alongside it in sibling
`covers/` and `data/` folders.

**Tip:** if a chosen cover index (`-m 1`) returns a non-English poster or
fails (the image was below TMDB's ~1000x1000 minimum size), just retry
with a different index (`-m 2`, `-m 3`, ...) until you get one you like.

### Uploading to Etsy (optional)

Only needed if you answer `y` at the `upload >` prompt. Requires a `.env`
file with `CLIENT_KEY`, `CLIENT_SECRET`, `RESOURCE_OWNER_KEY`, and
`RESOURCE_OWNER_SECRET` for Etsy's API (see `uploader.py`).
