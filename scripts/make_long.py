import os, json, uuid, sys, requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, AudioFileClip
from scripts.broll import fetch_broll

W, H = 1280, 720
SEGMENT = 50

FONT_PATH = "assets/fonts/TheSeasons.ttf"

def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

os.makedirs("long", exist_ok=True)

with open("data/news.json") as f:
    news = json.load(f)

news = news[:3]
clips = []

for item in news:
    query = " ".join(item["title"].split()[:3])
    video_url = fetch_broll(query)
    if not video_url:
        continue

    path = f"/tmp/{uuid.uuid4()}.mp4"
    open(path, "wb").write(requests.get(video_url).content)

    bg = (
        VideoFileClip(path)
        .resize(height=H)
        .subclip(0, SEGMENT)
    )

    img = Image.new("RGB", (W, H), "#f6f4f0")
    d = ImageDraw.Draw(img)

    y = 80
    for l in item["title"].split("."):
        d.text((60, y), l, fill="#222222", font=font(42))
        y += 48

    imgp = f"/tmp/{uuid.uuid4()}.png"
    img.save(imgp)

    clips.append(
        CompositeVideoClip([
            bg,
            ImageClip(imgp).set_duration(SEGMENT)
        ])
    )

final = concatenate_videoclips(clips)

music = "assets/music/news_theme.mp3"
if os.path.exists(music):
    final.audio = AudioFileClip(music).volumex(0.2)

out = f"long/{uuid.uuid4()}.mp4"
final.write_videofile(out, fps=24, codec="libx264", audio=True, logger=None)

print("✅ PROFESSIONAL LONG VIDEO CREATED:", out)
