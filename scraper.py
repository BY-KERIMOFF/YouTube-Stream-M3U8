import requests
from bs4 import BeautifulSoup
import json
import os

# Sayta sorğu göndəririk
url = 'https://www.ecanlitvizle.app'
response = requests.get(url)
html = response.text

# BeautifulSoup ilə HTML-i analiz edirik
soup = BeautifulSoup(html, 'html.parser')

# Kanal linklərini tapırıq (M3U linkləri)
channels = soup.find_all('a', href=True)  # bütün linkləri tapırıq

# M3U linklərini çıxarırıq
m3u_channels = []
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
