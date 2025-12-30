import requests, os, random

PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

def fetch_video(query):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_KEY,
        "q": query,
        "per_page": 5,
        "safesearch": True
    }

    r = requests.get(url, params=params, timeout=15).json()
    hits = r.get("hits", [])

    if not hits:
        return None

    video = random.choice(hits)
    return video["videos"]["medium"]["url"]
