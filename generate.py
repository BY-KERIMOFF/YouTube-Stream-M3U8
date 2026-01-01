#!/usr/bin/env python3
# YouTube JSON → M3U Generator
# By_Kerimoff

import json
import subprocess
import time
import os

OUTPUT_FILE = "youtube.m3u"

def get_m3u_from_youtube(search_query):
    try:
        cmd = [
            "yt-dlp",
            f"ytsearch1:{search_query}",
            "-g",
            "--no-warnings"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=20
        )
        url = result.stdout.strip()
        if url.startswith("http"):
            return url
    except Exception as e:
        print("Xəta:", e)
    return None

def main():
    with open("channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    m3u_lines = []
    m3u_lines.append("#EXTM3U")
    m3u_lines.append(f"#PLAYLIST:{data['playlist_name']}")
    m3u_lines.append(f"#GENERATED:{time.strftime('%Y-%m-%d %H:%M:%S')}")

    for channel in data["channels"]:
        name = channel["name"]
        search = channel["search"]

        print(f"[+] Axtarılır: {name}")
        m3u_url = get_m3u_from_youtube(search)

        if m3u_url:
            m3u_lines.append(f"#EXTINF:-1,{name}")
            m3u_lines.append(m3u_url)
            print(f"    ✔ Tapıldı")
        else:
            print(f"    ✘ Tapılmadı")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print("\n✔ M3U hazırdır:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
