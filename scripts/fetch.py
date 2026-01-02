import json
import subprocess
import os

CHANNEL_FILES = ["channels/tr.json"]
OUTPUT_FILE = "output/live.json"

def get_live_m3u8(channel_url):
    try:
        # yt-dlp istifadə olunur
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--skip-download",
            "-f", "best",
            "--get-url",
            channel_url
        ]
        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        # Canlı yayım varsa m3u8 linki çıxacaq
        if "m3u8" in result:
            return result
    except:
        pass
    return None  # Canlı yoxdursa None dön

all_channels = []

for file in CHANNEL_FILES:
    if not os.path.exists(file):
        continue

    with open(file, "r", encoding="utf-8") as f:
        channels = json.load(f)

    for ch in channels:
        m3u8 = get_live_m3u8(ch["youtube"])
        # 100% real canlı olanlar üçün əlavə olunur
        if m3u8:
            all_channels.append({
                "name": ch["name"],
                "youtube": ch["youtube"],
                "m3u8": m3u8,
                "status": "live"
            })

# output qovluğu yoxdursa yaradır
os.makedirs("output", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_channels, f, ensure_ascii=False, indent=2)

print("✅ Live JSON updated (only real live streams)")
