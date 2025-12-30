import os
import json
import uuid
import sys

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip

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

TITLE = item["title"]
DESC = (item.get("description") or "")[:120]

TEXT = f"{TITLE}\n\n{DESC}"

# ------------------------
# Create text image (PIL)
# ------------------------
WIDTH, HEIGHT = 1080, 1920
IMG = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
DRAW = ImageDraw.Draw(IMG)

# Default font (always exists on Linux)
FONT = ImageFont.load_default()

# Text box
MARGIN_X = 80
MARGIN_Y = 300
MAX_WIDTH = WIDTH - (MARGIN_X * 2)

def draw_multiline_text(draw, text, font, x, y, max_width, line_spacing=10):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + word + " "
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word + " "
    lines.append(current)

    for line in lines:
        draw.text((x, y), line, font=font, fill="white")
        y += font.size + line_spacing

draw_multiline_text(
    DRAW,
    TEXT,
    FONT,
    MARGIN_X,
    MARGIN_Y,
    MAX_WIDTH
)

# Save text image
img_path = f"/tmp/{uuid.uuid4()}.png"
IMG.save(img_path)

# ------------------------
# Build video
# ------------------------
DURATION = 30

bg = ColorClip((WIDTH, HEIGHT), color=(0, 0, 0), duration=DURATION)

txt_clip = (
    ImageClip(img_path)
    .set_duration(DURATION)
)

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
