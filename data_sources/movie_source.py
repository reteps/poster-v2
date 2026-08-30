import json
import os
import requests
import readline

"""
title:
release date:
rating:
runtime:
director:
writer:
categories:
plot:
"""

# IMDb now blocks scraping (imdbpy/Cinemagoer stopped working), so movie
# details are fetched from TMDB instead, using the same API key already
# used elsewhere in this project for cover art.
TMDB_API_KEY = os.environ.get(
    "TMDB_API_KEY", "4237f50f40774d6ed361922c222568a0")
TMDB_API_URL = "https://api.themoviedb.org/3"


def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()

    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


def select_plot(plots, num=None):

    plots = [p.split("::")[0] for p in plots]
    if num != None:
        return plots[num - 1]

    for i, plot in enumerate(plots[:8]):
        print(i + 1)
        print(plot)

    n = input("SELECT PLOT NUMBER > ")
    if "+" in n:
        n = n.replace("+", "")
        t = plots[int(n) - 1]
        return input_with_prefill("", t)
    return plots[int(n) - 1]


def _tmdb_get(path, params=None):
    params = {**(params or {}), "api_key": TMDB_API_KEY}
    r = requests.get(TMDB_API_URL + path, params=params)
    r.raise_for_status()
    return r.json()


def _find_movie_or_show(q):
    """Search TMDB for a movie first, falling back to TV, and return
    (tmdb_id, media_type)."""
    results = _tmdb_get("/search/movie", {"query": q}).get("results", [])
    results = [r for r in results if r.get(
        "release_date") or r.get("title")]
    if results:
        return results[0]["id"], "movie"
    results = _tmdb_get("/search/tv", {"query": q}).get("results", [])
    if results:
        return results[0]["id"], "tv"
    raise ValueError(f"No movie or TV show found for query: {q!r}")


def retrieve_movie_details(q):
    movieid, media_type = _find_movie_or_show(q)

    if media_type == "movie":
        details = _tmdb_get(
            f"/movie/{movieid}",
            {"append_to_response": "credits,release_dates"},
        )
    else:
        details = _tmdb_get(
            f"/tv/{movieid}",
            {"append_to_response": "credits,content_ratings"},
        )

    with open("out.txt", "w") as f:
        f.write(json.dumps(details, indent=2))

    title = details["title"] if media_type == "movie" else details["name"]
    print(title)

    crew = details.get("credits", {}).get("crew", [])
    cast = details.get("credits", {}).get("cast", [])

    if media_type == "movie":
        released_raw = details.get("release_date", "")
        year = released_raw[:4] if released_raw else ""
        released = _format_release_date(released_raw)
        h, m = divmod(int(details.get("runtime") or 0), 60)
        time_text = f"{h}h" if m == 0 else f"{h}h {m}min"
        rated = _movie_certification(details)
        directors = [c["name"] for c in crew if c.get("job") == "Director"]
        writers = [c["name"]
                   for c in crew if c.get("department") == "Writing"]
    else:
        released_raw = details.get("first_air_date", "")
        year = released_raw[:4] if released_raw else ""
        released = _format_release_date(released_raw)
        seasons = details.get("number_of_seasons", 1) or 1
        time_text = f"{seasons} season" + ("s" if seasons > 1 else "")
        rated = _tv_certification(details)
        directors = [c["name"]
                     for c in details.get("created_by", [])] or [
            c["name"] for c in crew if c.get("job") == "Director"
        ]
        writers = [c["name"] for c in crew if c.get(
            "department") == "Writing"]

    plots = [details.get("overview", "") or "No plot available."]

    data = {
        "original_title": title,
        "title": title,
        "released": released,
        "year": str(year),
        "tv": "TV" if media_type == "tv" else "Movie",
        "runtime": time_text,
        "director": directors[0] if directors else "error",
        "writers": list(dict.fromkeys(writers))[:4],
        "genres": [g["name"] for g in details.get("genres", [])][:3],
        "plots": plots,
        "id": movieid,
        "cast": [x["name"] for x in cast[:5]],
        "rated": rated,
    }
    return data


def _format_release_date(date_str):
    if not date_str:
        return ""
    from datetime import datetime

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%B %-d %Y")


def _movie_certification(details):
    results = details.get("release_dates", {}).get("results", [])
    us = next((r for r in results if r["iso_3166_1"] == "US"), None)
    if not us:
        return ""
    certs = [rd["certification"]
             for rd in us["release_dates"] if rd.get("certification")]
    return certs[0].lower() if certs else ""


def _tv_certification(details):
    results = details.get("content_ratings", {}).get("results", [])
    us = next((r for r in results if r["iso_3166_1"] == "US"), None)
    return us["rating"].lower() if us and us.get("rating") else ""


def modifier(movie_details, plot):
    if plot == None:
        plot = 1
    blacklist = {"plots", "cast", "id", "original_title"}
    movie_details["plot"] = movie_details["plots"][plot - 1].split("::")[0]
    intersection = sorted(list(set(movie_details) - blacklist))
    o = 0
    while True:
        try:
            os.system("clear")
            for i, k in enumerate(intersection):
                print(f"{i+1:2}| {k:10} | {movie_details[k]}")
            o = input("Option > ")
            if o == "":
                break
            o = int(o) - 1
            if o < 0 or o >= len(intersection):
                break
            key = intersection[o]
            detail = movie_details[key]
            if key == "plot":
                movie_details[key] = select_plot(movie_details["plots"])
            elif type(detail) == str:
                movie_details[key] = input(f"{key} ({detail}) > ")
            elif key == "writers":
                n = int(input("Keep N Writers. N > "))
                movie_details[key] = movie_details[key][:n]
        except ValueError:
            continue
    return movie_details
