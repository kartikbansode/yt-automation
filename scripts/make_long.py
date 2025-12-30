import os, json, uuid, sys, requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)

from broll import fetch_broll

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1280, 720
SEGMENT_DURATION = 45

BG_COLOR = "#f6f4f0"
TEXT_COLOR = "#222222"
FONT_PATH = "assets/fonts/TheSeasons.ttf"

TITLE_SIZE = 44
DESC_SIZE = 26

# ---------------- SETUP ----------------
os.makedirs("long", exist_ok=True)
os.makedirs("/tmp/media", exist_ok=True)

if not os.path.exists("data/news.json"):
    print("❌ news.json missing")
    sys.exit(0)

with open("data/news.json") as f:
    news = json.load(f)

news = news[:3]
if not news:
    print("⚠️ No news items")
    sys.exit(0)

def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

title_font = load_font(TITLE_SIZE)
desc_font = load_font(DESC_SIZE)

def wrap(draw, text, font, maxw):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = f"{line}{w} "
        if draw.textbbox((0,0), test, font=font)[2] <= maxw:
            line = test
        else:
            lines.append(line)
            line = f"{w} "
    lines.append(line)
    return lines

clips = []

# ---------------- BUILD SEGMENTS ----------------
for item in news:
    title = item.get("title", "")
    desc = item.get("description", "")

    query = " ".join(title.split()[:3])
    video_url = fetch_broll(query)

    bg_clip = None

    # -------- Try B-roll video --------
    if video_url:
        try:
            path = f"/tmp/media/{uuid.uuid4()}.mp4"
            open(path, "wb").write(requests.get(video_url, timeout=15).content)

            bg_clip = (
                VideoFileClip(path)
                .resize(height=HEIGHT)
                .subclip(0, min(SEGMENT_DURATION, VideoFileClip(path).duration))
            )
        except:
            bg_clip = None

    # -------- Fallback: Image slide --------
    if bg_clip is None:
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        y = 120
        for line in wrap(draw, title, title_font, WIDTH - 120):
            draw.text((60, y), line, fill=TEXT_COLOR, font=title_font)
            y += TITLE_SIZE + 6

        y += 20
        for line in wrap(draw, desc, desc_font, WIDTH - 120):
            draw.text((60, y), line, fill=TEXT_COLOR, font=desc_font)
            y += DESC_SIZE + 4

        img_path = f"/tmp/media/{uuid.uuid4()}.png"
        img.save(img_path)

        bg_clip = ImageClip(img_path).set_duration(SEGMENT_DURATION)

    # -------- Overlay text (light) --------
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (246, 244, 240, 120))
    overlay_path = f"/tmp/media/{uuid.uuid4()}.png"
    overlay.save(overlay_path)

    segment = CompositeVideoClip([
        bg_clip,
        ImageClip(overlay_path).set_duration(bg_clip.duration)
    ])

    clips.append(segment)

# ---------------- FINAL SAFETY CHECK ----------------
if not clips:
    print("⚠️ No segments created, skipping long video")
    sys.exit(0)

final = concatenate_videoclips(clips, method="compose")

# -------- Music (optional) --------
music_path = "assets/music/news_theme.mp3"
if os.path.exists(music_path):
    final.audio = AudioFileClip(music_path).volumex(0.25)

out = f"long/{uuid.uuid4()}.mp4"
final.write_videofile(out, fps=24, codec="libx264", audio=True, logger=None)

print("✅ PROFESSIONAL LONG VIDEO CREATED:", out)
