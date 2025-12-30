import requests, json, os

API_KEY = os.getenv("NEWS_API_KEY")
URL = "https://newsapi.org/v2/top-headlines?language=en"

os.makedirs("data", exist_ok=True)

r = requests.get(URL, params={"apiKey": API_KEY})
articles = r.json().get("articles", [])[:5]

news = []
for a in articles:
    news.append({
        "title": a.get("title", ""),
        "description": a.get("description", ""),
        "image": a.get("urlToImage", "")
    })

with open("data/news.json", "w") as f:
    json.dump(news, f, indent=2)
