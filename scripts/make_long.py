import os
import json
import uuid
import sys

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips, ColorClip

# ------------------------
# Constants
# ------------------------
WIDTH, HEIGHT = 1280, 720   # YouTube long format (16:9)
CLIP_DURATION = 60          # seconds per news item
LINE_SPACING = 10
MARGIN_X = 60
START_Y = 120

# ------------------------
# Setup
# ------------------------
os.makedirs("long", exist_ok=True)

if not os.path.exists("data/news.json"):
    print("❌ data/news.json not found")
    sys.exit(0)

with open("data/news.json", "r") as f:
    news = json.load(f)

if not news:
    print("⚠️ news.json is empty")
    sys.exit(0)

# Use top 3–5 news items
news_items = news[:3]

font = ImageFont.load_default()

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = f"{current}{word} "
        if text_width(draw, test, font) <= max_width:
            current = test
        else:
            lines.append(current.rstrip())
            current = f"{word} "
    if current:
        lines.append(current.rstrip())

    return lines

clips = []

# ------------------------
# Generate slides
# ------------------------
for idx, item in enumerate(news_items, start=1):
    title = item.get("title", "").strip()
    desc = (item.get("description") or "").strip()

    text_blocks = [
        f"News {idx}",
        "",
        title,
        "",
        desc
    ]

    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    MAX_WIDTH = WIDTH - (MARGIN_X * 2)
    y = START_Y

    for block in text_blocks:
        if not block:
            y += font.size * 2
            continue

        lines = wrap_text(draw, block, font, MAX_WIDTH)
        for line in lines:
            draw.text((MARGIN_X, y), line, fill="white", font=font)
            y += font.size + LINE_SPACING

    img_path = f"/tmp/{uuid.uuid4()}.png"
    img.save(img_path)

    slide = (
        ImageClip(img_path)
        .set_duration(CLIP_DURATION)
    )

    clips.append(slide)

# ------------------------
# Concatenate into final video
# ------------------------
final_video = concatenate_videoclips(clips, method="compose")

output_file = f"long/{uuid.uuid4()}.mp4"

final_video.write_videofile(
    output_file,
    fps=24,
    codec="libx264",
    audio=False,
    verbose=False,
    logger=None
)

print("✅ Long video created:", output_file)
