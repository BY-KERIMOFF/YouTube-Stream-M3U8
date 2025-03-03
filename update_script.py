import requests
from bs4 import BeautifulSoup

# URL tərtib et
url = 'https://www.ecanlitvizle.app/xezer-tv-canli-izle/'

# Saytı çək
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Linki tapmaq
script_tag = soup.find('script', string=lambda t: t and 'tkn=' in t)  # 'text' əvəzinə 'string' istifadə edin

if script_tag:
    # Tokeni çıxar
    script_content = script_tag.string
    token_start = script_content.find('tkn=') + 4  # 'tkn=' ifadəsindən sonra başlayır
    token_end = script_content.find('&', token_start)  # '&' simvoluna qədər davam edir
    token = script_content[token_start:token_end]  # Tokeni çıxar

    with open('token.txt', 'w') as file:
        file.write(token)
    print("✅ Token tapıldı.")

    # Yeni link yarat
    new_link = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740980455"
    with open("stream.m3u8", "w") as file:
        file.write(new_link)
    print("✅ stream.m3u8 yeniləndi.")
else:
    print("❌ Token tapılmadı.")
    
    # Əgər token tapılmasa, sabit link əlavə et
    with open("stream.m3u8", "w") as file:
        file.write("https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=w3nxqj5RKo4JLfvPLv9oxA&tms=1740980455")
    print("✅ stream.m3u8 sabit link ilə yeniləndi.")
