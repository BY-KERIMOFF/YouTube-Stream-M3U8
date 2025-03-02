import requests
from bs4 import BeautifulSoup
import json
import os

# M3U linklərini tapmaq üçün URL-lər
urls = [
    "https://www.ecanlitvizle.app/xezer-tv-canli-izle/",
    "https://www.ecanlitvizle.app/show-tv-canli-izle-hd-4/",
    "https://www.ecanlitvizle.app/tlc-tv-canli/"
]

# M3U linklərini saxlamaq üçün siyahı
m3u_channels = []

# URL-ləri dövr edirik
for url in urls:
    response = requests.get(url)
    html = response.text

    # Saytın HTML-i ilə işləyirik
    soup = BeautifulSoup(html, 'html.parser')

    # M3U linklərini tapırıq
    channels = soup.find_all('a', href=True)  # Bütün linkləri tapırıq

    for channel in channels:
        href = channel['href']
        if '.m3u' in href:  # Yalnız M3U linklərini tapırıq
            name = channel.text.strip()  # Kanalın adı
            m3u_channels.append({
                'name': name,
                'm3u_url': href  # M3U linkini saxlayırıq
            })

# JSON faylını yazırıq
output_path = os.path.join(os.getcwd(), 'channels.json')
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(m3u_channels, file, ensure_ascii=False, indent=4)

print(f'JSON faylı yaradıldı: {output_path}')
