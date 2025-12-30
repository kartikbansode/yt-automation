from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import json, uuid, os

os.makedirs("shorts", exist_ok=True)

with open("data/news.json") as f:
    news = json.load(f)

item = news[0]

text = f"{item['title']}\n\n{item['description'][:120]}"

bg = ColorClip(size=(1080,1920), color=(0,0,0)).set_duration(30)

txt = TextClip(
    text,
    fontsize=48,
    color="white",
    size=(900,1600),
    method="caption",
    align="center"
).set_duration(30)

final = CompositeVideoClip([bg, txt.set_position("center")])

filename = f"shorts/{uuid.uuid4()}.mp4"
final.write_videofile(
    filename,
    fps=24,
    codec="libx264",
    audio=False
)

print("Created short:", filename)
