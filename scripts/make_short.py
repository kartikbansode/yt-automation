import os, json, uuid, sys, requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip
from scripts.broll import fetch_broll

# ---------- CONFIG ----------
W, H = 1080, 1920
DURATION = 32
BG_COLOR = "#f6f4f0"
TXT_COLOR = "#222222"

FONT_PATH = "assets/fonts/TheSeasons.ttf"
TITLE_SIZE = 84
DESC_SIZE = 44

# ---------- SETUP ----------
os.makedirs("shorts", exist_ok=True)
os.makedirs("/tmp/media", exist_ok=True)

with open("data/news.json") as f:
    news = json.load(f)

if not news:
    sys.exit(0)

item = news[0]
title = item["title"]
desc = (item.get("description") or "")[:140]

# ---------- FONT ----------
def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

# ---------- VIDEO ----------
query = " ".join(title.split()[:3])
video_url = fetch_broll(query)

if not video_url:
    print("No b-roll found")
    sys.exit(0)

video_path = f"/tmp/media/{uuid.uuid4()}.mp4"
open(video_path, "wb").write(requests.get(video_url).content)

bg_video = (
    VideoFileClip(video_path)
    .resize(height=H)
    .crop(x_center=W//2, y_center=H//2, width=W, height=H)
    .subclip(0, DURATION)
)

# ---------- TEXT IMAGE ----------
img = Image.new("RGB", (W, H), BG_COLOR)
draw = ImageDraw.Draw(img)

def wrap(text, f, maxw):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = f"{line}{w} "
        if draw.textbbox((0,0), test, font=f)[2] <= maxw:
            line = test
        else:
            lines.append(line)
            line = f"{w} "
    lines.append(line)
    return lines

y = 260
for l in wrap(title, font(TITLE_SIZE), W-160):
    draw.text((80, y), l, fill=TXT_COLOR, font=font(TITLE_SIZE))
    y += TITLE_SIZE + 6

y += 30
for l in wrap(desc, font(DESC_SIZE), W-160):
    draw.text((80, y), l, fill=TXT_COLOR, font=font(DESC_SIZE))
    y += DESC_SIZE + 4

img_path = f"/tmp/media/{uuid.uuid4()}.png"
img.save(img_path)

text_clip = ImageClip(img_path).set_duration(DURATION)

# ---------- MUSIC ----------
music_path = "assets/music/news_theme.mp3"
if os.path.exists(music_path):
    audio = AudioFileClip(music_path).volumex(0.25).set_duration(DURATION)
else:
    audio = None

final = CompositeVideoClip([bg_video, text_clip])
if audio:
    final.audio = audio

out = f"shorts/{uuid.uuid4()}.mp4"
final.write_videofile(out, fps=24, codec="libx264", audio=True, logger=None)

print("✅ PROFESSIONAL SHORT CREATED:", out)
