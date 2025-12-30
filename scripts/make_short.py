import os
import json
import uuid
import sys

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip

# ------------------------
# Constants
# ------------------------
WIDTH, HEIGHT = 1080, 1920
DURATION = 30
MARGIN_X = 80
START_Y = 300
LINE_SPACING = 12

# ------------------------
# Setup
# ------------------------
os.makedirs("shorts", exist_ok=True)

if not os.path.exists("data/news.json"):
    print("❌ data/news.json not found")
    sys.exit(0)

with open("data/news.json", "r") as f:
    news = json.load(f)

if not news:
    print("⚠️ news.json is empty")
    sys.exit(0)

item = news[0]

title = item.get("title", "").strip()
desc = (item.get("description") or "").strip()[:140]

text_blocks = [title, "", desc]

# ------------------------
# Create image
# ------------------------
img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

MAX_WIDTH = WIDTH - (MARGIN_X * 2)

def text_width(draw, text, font):
    """Return width of single-line text using Pillow >=10"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def wrap_line(draw, text, font, max_width):
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

y = START_Y

for block in text_blocks:
    if not block:
        y += font.size * 2
        continue

    lines = wrap_line(draw, block, font, MAX_WIDTH)
    for line in lines:
        draw.text((MARGIN_X, y), line, fill="white", font=font)
        y += font.size + LINE_SPACING

# ------------------------
# Save image
# ------------------------
img_path = f"/tmp/{uuid.uuid4()}.png"
img.save(img_path)

# ------------------------
# Build video
# ------------------------
bg = ColorClip((WIDTH, HEIGHT), color=(0, 0, 0), duration=DURATION)
txt_clip = ImageClip(img_path).set_duration(DURATION)

final = CompositeVideoClip([bg, txt_clip])

out_file = f"shorts/{uuid.uuid4()}.mp4"

final.write_videofile(
    out_file,
    fps=24,
    codec="libx264",
    audio=False,
    verbose=False,
    logger=None
)

print("✅ Short created:", out_file)
