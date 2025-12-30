import os, json, uuid, sys, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import ImageClip, CompositeVideoClip

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1080, 1920
DURATION = 30

BG_COLOR = "#f6f4f0"
TEXT_COLOR = "#222222"
OVERLAY_ALPHA = 160

FONT_PATH = "assets/fonts/TheSeasons.ttf"
TITLE_SIZE = 88
DESC_SIZE = 46

# ---------------- SETUP ----------------
os.makedirs("shorts", exist_ok=True)
os.makedirs("assets/images", exist_ok=True)

with open("data/news.json") as f:
    news = json.load(f)

if not news:
    print("No news available")
    sys.exit(0)

item = news[0]
title = item["title"]
desc = (item.get("description") or "")[:160]
img_url = item.get("image")

# ---------------- FONT ----------------
def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

title_font = load_font(TITLE_SIZE)
desc_font = load_font(DESC_SIZE)

# ---------------- IMAGE ----------------
bg = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

if img_url:
    try:
        r = requests.get(img_url, timeout=10)
        img_path = f"assets/images/{uuid.uuid4()}.jpg"
        with open(img_path, "wb") as f:
            f.write(r.content)

        img = Image.open(img_path).convert("RGB")
        img = img.resize((WIDTH, HEIGHT))
        img = img.filter(ImageFilter.GaussianBlur(12))
        bg.paste(img, (0, 0))
    except:
        pass

# Overlay
overlay = Image.new("RGBA", (WIDTH, HEIGHT), (246, 244, 240, OVERLAY_ALPHA))
bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

draw = ImageDraw.Draw(bg)

# ---------------- TEXT WRAP ----------------
def wrap(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = f"{line}{w} "
        if draw.textbbox((0,0), test, font=font)[2] <= max_width:
            line = test
        else:
            lines.append(line)
            line = f"{w} "
    lines.append(line)
    return lines

y = 280
for line in wrap(draw, title, title_font, WIDTH - 160):
    draw.text((80, y), line, font=title_font, fill=TEXT_COLOR)
    y += TITLE_SIZE + 8

y += 40
for line in wrap(draw, desc, desc_font, WIDTH - 160):
    draw.text((80, y), line, font=desc_font, fill=TEXT_COLOR)
    y += DESC_SIZE + 6

# ---------------- EXPORT ----------------
img_path = f"/tmp/{uuid.uuid4()}.png"
bg.convert("RGB").save(img_path)

video = CompositeVideoClip([
    ImageClip(img_path).set_duration(DURATION)
])

out = f"shorts/{uuid.uuid4()}.mp4"
video.write_videofile(out, fps=24, codec="libx264", audio=False, logger=None)

print("✅ PRO Short created:", out)
