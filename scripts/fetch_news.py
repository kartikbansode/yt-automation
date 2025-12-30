import requests, json, os

API_KEY = os.getenv("NEWS_API_KEY")
URL = "https://newsapi.org/v2/top-headlines?language=en"

r = requests.get(URL, params={"apiKey": API_KEY})
articles = r.json().get("articles", [])[:5]

news = []
for a in articles:
    news.append({
        "title": a["title"],
        "description": a["description"] or "",
        "image": a["urlToImage"]
    })

with open("data/news.json", "w") as f:
    json.dump(news, f, indent=2)
