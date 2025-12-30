from moviepy.editor import *
import json, uuid, os

with open("data/news.json") as f:
    news = json.load(f)

item = news[0]

text = f"{item['title']}\n\n{item['description'][:120]}"

clip = TextClip(
    text,
    fontsize=48,
    color="white",
    size=(1080,1920),
    method="caption",
    align="center"
).set_duration(30)

bg = ColorClip(size=(1080,1920), color=(0,0,0)).set_duration(30)
final = CompositeVideoClip([bg, clip])

filename = f"shorts/{uuid.uuid4()}.mp4"
final.write_videofile(filename, fps=24)

print("Created short:", filename)
