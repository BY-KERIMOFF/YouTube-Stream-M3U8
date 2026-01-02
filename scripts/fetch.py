import json
import subprocess
import os

CHANNEL_FILES = ["channels/tr.json"]
OUTPUT_FILE = "output/live.json"

# Proxy URL (istəsən dəyişə bilərsən)
PROXY = os.environ.get("PROXY", "http://cors.tundracast.com:2000/")

def get_live_m3u8(channel_url):
    """
    YouTube-dan son canlı yayımın .m3u8 linkini çıxarır.
    """
    try:
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--skip-download",
            "--quiet",
            "--get-url",
            "--socket-timeout", "15",
            channel_url
        ]
        if PROXY:
            cmd.extend(["--proxy", PROXY])

        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=20).decode().strip()
        if "m3u8" in result:
            return result
    except subprocess.TimeoutExpired:
        print(f"⏱ Timeout: {channel_url}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

all_channels = []

for file in CHANNEL_FILES:
    if not os.path.exists(file):
        continue

    with open(file, "r", encoding="utf-8") as f:
        channels = json.load(f)

    for ch in channels:
        m3u8 = get_live_m3u8(ch["youtube"])
        if m3u8:
            all_channels.append({
                "name": ch["name"],
                "youtube": ch["youtube"],
                "m3u8": m3u8,
                "status": "live"
            })

os.makedirs("output", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_channels, f, ensure_ascii=False, indent=2)

print("✅ Live JSON updated (Show TV & Kanal 7 real-time)")
