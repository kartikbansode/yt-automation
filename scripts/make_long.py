import os, json, uuid, sys, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import ImageClip, concatenate_videoclips

WIDTH, HEIGHT = 1280, 720
DURATION = 50

BG_COLOR = "#f6f4f0"
TEXT_COLOR = "#222222"

FONT_PATH = "assets/fonts/TheSeasons.ttf"
TITLE_SIZE = 52
DESC_SIZE = 30

os.makedirs("long", exist_ok=True)
os.makedirs("assets/images", exist_ok=True)

with open("data/news.json") as f:
    news = json.load(f)

news = news[:3]
if not news:
    sys.exit(0)

def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

title_font = load_font(TITLE_SIZE)
desc_font = load_font(DESC_SIZE)

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

clips = []

for item in news:
    bg = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

    if item.get("image"):
        try:
            r = requests.get(item["image"], timeout=10)
            img = Image.open(r.raw).convert("RGB")
            img = img.resize((WIDTH, HEIGHT)).filter(ImageFilter.GaussianBlur(10))
            bg.paste(img)
        except:
            pass

    draw = ImageDraw.Draw(bg)
    y = 120

    for line in wrap(draw, item["title"], title_font, WIDTH - 120):
        draw.text((60, y), line, font=title_font, fill=TEXT_COLOR)
        y += TITLE_SIZE + 6

    y += 20
    for line in wrap(draw, item.get("description",""), desc_font, WIDTH - 120):
        draw.text((60, y), line, font=desc_font, fill=TEXT_COLOR)
        y += DESC_SIZE + 4

    img_path = f"/tmp/{uuid.uuid4()}.png"
    bg.save(img_path)

    clips.append(ImageClip(img_path).set_duration(DURATION))

final = concatenate_videoclips(clips)
out = f"long/{uuid.uuid4()}.mp4"
final.write_videofile(out, fps=24, codec="libx264", audio=False, logger=None)

print("✅ PRO Long video created:", out)
