import sys, os, json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

video_type = sys.argv[1]

folder = "shorts" if video_type == "short" else "long"
file = sorted(os.listdir(folder))[-1]

with open("config/youtube.json") as f:
    cfg = json.load(f)

creds = Credentials.from_authorized_user_file(
    "config/token.json",
    ["https://www.googleapis.com/auth/youtube.upload"]
)

youtube = build("youtube", "v3", credentials=creds)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": cfg[video_type]["title"],
            "description": cfg[video_type]["description"],
            "tags": cfg[video_type]["hashtags"]
        },
        "status": {"privacyStatus": "public"}
    },
    media_body=MediaFileUpload(f"{folder}/{file}")
)

request.execute()
print("Uploaded:", file)
