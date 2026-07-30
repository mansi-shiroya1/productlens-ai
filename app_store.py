"""
Fetch real App Store data via iTunes Search API (no auth required).
Falls back gracefully if unavailable.
"""
import requests
import re

def fetch_app_store_data(product_name: str) -> dict | None:
    """Query iTunes Search API for real app metadata."""
    try:
        url = "https://itunes.apple.com/search"
        params = {
            "term": product_name,
            "entity": "software",
            "limit": 1,
            "country": "us"
        }
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("results"):
            return None

        app = data["results"][0]
        rating = app.get("averageUserRating")
        rating_count = app.get("userRatingCount", 0)
        price = app.get("formattedPrice", "Free")
        genre = app.get("primaryGenreName", "")
        developer = app.get("artistName", "")
        app_name = app.get("trackName", product_name)

        if not rating:
            return None

        # Format rating count
        if rating_count >= 1_000_000:
            rating_fmt = f"{rating_count/1_000_000:.1f}M"
        elif rating_count >= 1_000:
            rating_fmt = f"{rating_count/1_000:.0f}K"
        else:
            rating_fmt = str(rating_count)

        return {
            "app_name": app_name,
            "rating": round(rating, 1),
            "rating_count": rating_fmt,
            "price": price,
            "genre": genre,
            "developer": developer,
            "real_data": True
        }
    except Exception:
        return None
