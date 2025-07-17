import json
from yt_dlp import YoutubeDL

def get_m3u8(youtube_url):
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'format': 'best[protocol^=m3u8_native]/best'
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        for fmt in info.get("formats", []):
            if "m3u8" in fmt.get("protocol", ""):
                return fmt["url"]
    return None

def main():
    with open("channels.json", "r", encoding="utf-8") as f:
        channels = json.load(f)["channels"]

    output = []
    for ch in channels:
        m3u8_link = get_m3u8(ch["url"])
        output.append({
            "name": ch["name"],
            "slug": ch["slug"],
            "m3u8": m3u8_link or "Not found"
        })

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
