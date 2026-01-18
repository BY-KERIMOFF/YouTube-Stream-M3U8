import requests
import re

# Browser request kimi göndəriləcək headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}

# Token alma URL-i (browser request-dən çıxardığın URL)
token_url = "https://cdn505.canlitv.me/live/bloomberght-hd-live"

# GET sorğu göndər
r = requests.get(token_url, headers=headers)
html = r.text

# Tokeni regex ilə çıxar
# (məsələn: tkn=...)
match = re.search(r'tkn=([A-Za-z0-9_-]+)', html)
if match:
    token = match.group(1)
    print("Yeni token:", token)
else:
    print("Token tapılmadı")
    token = "INITIAL_TOKEN"

# Yeni playlist yaradırıq
playlist_content = f"""#EXTM3U
#EXTINF:-1,Bloomberg HT
https://cdn505.canlitv.me/bloomberght.m3u8?tkn={token}&other_params
"""

# Playlisti yenilə
with open("playlist.m3u8", "w") as f:
    f.write(playlist_content)
