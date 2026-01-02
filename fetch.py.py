import json
import subprocess
import os

CHANNEL_FILES = [
    "channels/tr.json",
    "channels/az.json",
    "channels/ru.json"
]

OUTPUT_FILE = "output/live.json"

def get_m3u8(url):
    try:
        cmd = [
            "yt-dlp",
            "-f", "best",
            "--print", "%(url)s",
            url
        ]
        result = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL
        ).decode().strip()

        if "m3u8" in result:
            return result
    except:
        pass

    return None

all_channels = []

for file in CHANNEL_FILES:
    if not os.path.exists(file):
        continue

    with open(file, "r", encoding="utf-8") as f:
        channels = json.load(f)

    for ch in channels:
        m3u8 = get_m3u8(ch["youtube"])
        all_channels.append({
            "name": ch["name"],
            "youtube": ch["youtube"],
            "m3u8": m3u8,
            "status": "live" if m3u8 else "offline"
        })

os.makedirs("output", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_channels, f, ensure_ascii=False, indent=2)

print("DONE")
