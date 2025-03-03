import requests
from bs4 import BeautifulSoup

# Yeni URL
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# URL'yi əldə et
response = requests.get(url)

# Əgər səhv cavab almışıqsa, dayandırırıq
if response.status_code != 200:
    print("❌ Saytın məzmunu alınmadı!")
    exit(1)

# HTML məzmununu BeautifulSoup ilə parse edirik
soup = BeautifulSoup(response.text, 'html.parser')

# Script tagi içində 'tkn=' olan bir yazını tapmağa çalışırıq
script_tag = soup.find('script', text=lambda t: t and 'tkn=' in t)

# Token tapılmasa belə, çıxarmağa çalışacağıq
if script_tag:
    try:
        token = script_tag.string.split('tkn=')[1].split('"')[0]
        print(f"✅ Yeni token tapıldı: {token}")
    except IndexError:
        print("❌ Tokeni tapmaq mümkün olmadı.")
else:
    print("❌ Token tapılmadı.")

# İndi, yeni stream.m3u8 linkini yaratmağa çalışırıq
# Əgər token tapılıbsa, istifadə edirik, əks halda default token əlavə edirik.
if 'token' in locals():
    new_link = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740969806"
else:
    new_link = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=default_token&tms=1740969806"

# Linki çap edirik
print(f"✅ Stream linki: {new_link}")
