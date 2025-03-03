import requests
from bs4 import BeautifulSoup

# URL tərtib et
url = 'https://www.ecanlitvizle.app/xezer-tv-canli-izle/'

# Saytı çək
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Linki tapmaq
script_tag = soup.find('script', text=lambda t: t and 'tkn=' in t)

if script_tag:
    # Tokeni çıxar
    token = script_tag.string.split('tkn=')[1].split('"')[0]
    with open('token.txt', 'w') as file:
        file.write(token)
    print("✅ Token tapıldı.")

    # Yeni link yarat
    new_link = f"https://example.com/stream.m3u8?tkn={token}"
    with open("stream.m3u8", "w") as file:
        file.write(new_link)
    print("✅ stream.m3u8 yeniləndi.")
else:
    print("❌ Token tapılmadı.")
    
    # Əgər token tapılmasa, yeni link əlavə et
    with open("stream.m3u8", "w") as file:
        file.write("https://new-link.example.com/stream.m3u8")
    print("✅ stream.m3u8 yeniləndi.")
