import requests

# Yeni token URL-ni təyin edirik (Sadəcə nümunə olaraq)
NEW_TOKEN = "newTokenValue"  # Burada yeni tokeni və ya digər parametrləri əlavə edin
NEW_M3U8 = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={NEW_TOKEN}&tms=1740969806"

# stream.m3u8 faylını yeni link ilə yeniləyirik
with open("stream.m3u8", "w") as f:
    f.write(NEW_M3U8)

print("✅ stream.m3u8 faylı yeni link ilə yeniləndi.")
