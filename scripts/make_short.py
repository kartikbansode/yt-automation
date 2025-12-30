import os
import json
import uuid
import sys

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip

# ------------------------
# Setup
# ------------------------
WIDTH, HEIGHT = 1080, 1920
DURATION = 30

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
# Create PIL image
# ------------------------
img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

MARGIN_X = 80
START_Y = 300
LINE_SPACING = 12
MAX_WIDTH = WIDTH - (MARGIN_X * 2)

def wrap_line(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test_line = f"{current}{word} "
        w, _ = draw.textsize(test_line, font=font)
        if w <= max_width:
            current = test_line
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

    wrapped = wrap_line(draw, block, font, MAX_WIDTH)
    for line in wrapped:
        draw.text((MARGIN_X, y), line, fill="white", font=font)
        y += font.size + LINE_SPACING

# ------------------------
# Save text image
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
