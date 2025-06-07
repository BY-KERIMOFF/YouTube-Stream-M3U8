import json
import subprocess
from pathlib import Path

with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

lines = ["#EXTM3U"]

for ch in channels:
    name = ch["name"]
    url = ch["url"]
    print(f"[+] Yoxlanır: {name}")
    try:
        result = subprocess.run([
            "yt-dlp", "-g", "--cookies", "cookies.txt", url
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

        m3u8 = result.stdout.strip()
        if m3u8.startswith("http"):
            lines.append(f"#EXTINF:-1,{name}\n{m3u8}")
            print(f"    ✅ {name} əlavə olundu.")
        else:
            print(f"    ❌ Stream tapılmadı.")
    except Exception as e:
        print(f"    ❌ Xəta: {e}")

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("\n🎉 Hazırlandı: playlist.m3u")
