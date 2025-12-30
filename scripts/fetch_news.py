import os
import json
import requests
import sys

API_KEY = os.getenv("NEWS_API_KEY")

if not API_KEY:
    print("❌ NEWS_API_KEY not set")
    sys.exit(0)

URL = "https://newsapi.org/v2/top-headlines"

params = {
    "apiKey": API_KEY,
    "language": "en",
    "pageSize": 10
}

os.makedirs("data", exist_ok=True)

try:
    response = requests.get(URL, params=params, timeout=15)
    data = response.json()
except Exception as e:
    print("❌ Network/API error:", e)
    sys.exit(0)

if data.get("status") != "ok":
    print("❌ News API error:", data)
    sys.exit(0)

articles = data.get("articles", [])

news = []
for a in articles:
    title = a.get("title")
    description = a.get("description")

    if not title or not description:
        continue

    news.append({
        "title": title.strip(),
        "description": description.strip(),
        "image": a.get("urlToImage", "")
    })

if not news:
    print("⚠️ No valid news articles after filtering")
    sys.exit(0)

with open("data/news.json", "w") as f:
    json.dump(news, f, indent=2)

print(f"✅ Saved {len(news)} news items to data/news.json")
