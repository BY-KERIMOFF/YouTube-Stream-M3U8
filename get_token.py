import requests
from bs4 import BeautifulSoup

# Hedef URL
url = 'https://www.ecanlitvizle.app/xezer-tv-canli-izle/'

# Request göndəririk
response = requests.get(url)
if response.status_code != 200:
    print("❌ Səhifə tapılmadı!")
    exit(1)

# BeautifulSoup ilə səhifəni parse edirik
soup = BeautifulSoup(response.content, 'html.parser')

# Tokeni tapmaq üçün script içərisindəki məlumatı axtarırıq
script_tag = soup.find('script', text=lambda t: t and 'tkn=' in t)

if script_tag:
    # Tokeni tapmaq
    token = script_tag.text.split('tkn=')[1].split('&')[0]
    print(f"✅ Token tapıldı: {token}")
else:
    print("❌ Token tapılmadı, yeni link ilə yeniləyirik.")
    token = 'new_token_placeholder'  # Token tapılmadısa, buraya yer saxlayırıq

# stream.m3u8 faylını yeniləyirik
new_m3u8_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740969806"

# stream.m3u8 faylını yeniləyirik
with open("stream.m3u8", "w") as file:
    file.write(new_m3u8_url)

print("✅ stream.m3u8 yeniləndi.")
