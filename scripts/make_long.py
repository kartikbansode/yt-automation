from moviepy.editor import *
import json, uuid

os.makedirs("long", exist_ok=True)


with open("data/news.json") as f:
    news = json.load(f)

clips = []
for item in news[:3]:
    txt = f"{item['title']}\n\n{item['description']}"
    clip = TextClip(
        txt,
        fontsize=36,
        color="white",
        size=(1280,720),
        method="caption"
    ).set_duration(60)
    clips.append(clip)

final = concatenate_videoclips(clips)
filename = f"long/{uuid.uuid4()}.mp4"
final.write_videofile(filename, fps=24)

print("Created long video:", filename)
