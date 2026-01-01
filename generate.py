#!/usr/bin/env python3
# YouTube Live JSON → M3U (FIXED)
# By_Kerimoff

import json
import subprocess
import time

OUTPUT_FILE = "youtube.m3u"

def run(cmd, timeout=20):
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )

def find_live_video_id(search):
    """
    YouTube-da canlı yayım video ID tapır
    """
    try:
        cmd = [
            "yt-dlp",
            f"ytsearch5:{search}",
            "--dump-json",
            "--no-warnings"
        ]
        r = run(cmd, 20)

        for line in r.stdout.splitlines():
            info = json.loads(line)
            if info.get("is_live"):
                return info["id"]
    except:
        pass
    return None

def get_m3u_from_video_id(video_id):
    """
    Video ID → m3u8 URL
    """
    try:
        cmd = [
            "yt-dlp",
            "-g",
            f"https://www.youtube.com/watch?v={video_id}",
            "--no-warnings"
        ]
        r = run(cmd, 20)
        url = r.stdout.strip()
        if url.startswith("http"):
            return url
    except:
        pass
    return None

def main():
    with open("channels.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = [
        "#EXTM3U",
        f"#PLAYLIST:{data['playlist_name']}",
        f"#GENERATED:{time.strftime('%Y-%m-%d %H:%M:%S')}"
    ]

    for ch in data["channels"]:
        name = ch["name"]
        search = ch["search"]

        print(f"[+] Axtarılır: {name}")
        video_id = find_live_video_id(search)

        if not video_id:
            print("    ✘ Canlı tapılmadı")
            continue

        m3u = get_m3u_from_video_id(video_id)
        if not m3u:
            print("    ✘ M3U alına bilmədi")
            continue

        lines.append(f"#EXTINF:-1,{name}")
        lines.append(m3u)
        print("    ✔ CANLI ƏLAVƏ EDİLDİ")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n✔ M3U hazırdır:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
