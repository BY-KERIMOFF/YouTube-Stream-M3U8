import requests
from bs4 import BeautifulSoup

# Yeni linki tapmaq üçün sayt
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Saytı açırıq
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Tokeni tapmaq üçün scriptdən məlumatı çəkirik
try:
    script_tag = soup.find('script', text=lambda t: t and 'tkn=' in t)
    token = script_tag.string.split('tkn=')[1].split("'")[0]  # Tokeni çıxarırıq
    print(f"✅ Token tapıldı: {token}")
    
    # stream.m3u8 faylını yeniləyirik
    new_m3u8 = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740969806"
    
    with open("stream.m3u8", "w") as file:
        file.write(new_m3u8)
    print("✅ stream.m3u8 faylı yeniləndi.")
except Exception as e:
    print("❌ Token tapılmadı, yeni link ilə yeniləyirik.")
    # Token tapılmadıqda yeni linki qeyd edirik
    fallback_m3u8 = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=fallback_token&tms=1740969806"
    
    with open("stream.m3u8", "w") as file:
        file.write(fallback_m3u8)
    print("✅ stream.m3u8 faylı yeniləndi (fallback).")
