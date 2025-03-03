import requests
from bs4 import BeautifulSoup

# Yeni URL
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# URL'yi əldə edirik
response = requests.get(url)

# Əgər səhv cavab almışıqsa, dayandırırıq
if response.status_code != 200:
    print("❌ Saytın məzmunu alınmadı!")
    exit(1)

# HTML məzmununu BeautifulSoup ilə parse edirik
soup = BeautifulSoup(response.text, 'html.parser')

# Linki axtarırıq
link = None

# Web səhifəsindən stream.m3u8 linkini tapmaq
for script in soup.find_all('script'):
    if 'tkn=' in str(script):
        # 'tkn=' olan hissəni tapıb linki çıxardırıq
        try:
            link = str(script).split('tkn=')[1].split('"')[0]
            break
        except IndexError:
            print("❌ Token tapılmadı, amma linki yeniləyirik.")

# Əgər tapmadıqsa, yəni tkn tapılmadısa, linki əvəz edirik
if not link:
    # Bura default olaraq stream.m3u8 linki verirəm
    link = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=default_token&tms=1740969806"

print(f"✅ Yenilənmiş stream.m3u8 linki: {link}")
