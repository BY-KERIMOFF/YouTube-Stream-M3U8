import requests

# Token almaq üçün URL
token_url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# M3U8 formatında linkin əsası
base_m3u8_url = "https://ecanlitv3.etvserver.com/xazartv.m3u8"

# Tokeni əldə et (sənin mövcud metodunla dəyişdir)
token = "JCm4CeptUoCkaoqwLPifNQ"  # Bunu avtomatik tapmaq üçün kodunu əlavə et

# Yeni M3U8 linkini yarat
new_m3u8_link = f"{base_m3u8_url}?tkn={token}&tms=1740967951"

# M3U8 faylına yazmaq
m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=300000
{new_m3u8_link}
"""

with open("stream.m3u8", "w") as file:
    file.write(m3u8_content)

print("✅ Yeni M3U8 faylı yaradıldı: stream.m3u8")
