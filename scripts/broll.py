import requests, os, random

API_KEY = os.getenv("PIXABAY_API_KEY")

def fetch_broll(query):
    if not API_KEY:
        return None

    url = "https://pixabay.com/api/videos/"
    params = {
        "key": API_KEY,
        "q": query,
        "per_page": 10,
        "safesearch": True
    }

    r = requests.get(url, params=params, timeout=15).json()
    hits = r.get("hits", [])

    if not hits:
        return None

    video = random.choice(hits)
    return video["videos"]["medium"]["url"]
