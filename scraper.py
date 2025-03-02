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

# Kanal linklərini tapırıq (XPath ilə deyil, CSS selector ilə)
channels = soup.find_all('a', class_='channel-link')  # Bu sinifi təhlil etməli olacaqsınız

# Kanal məlumatlarını toplamaq
channel_list = []
for channel in channels:
    name = channel.text.strip()
    url = channel.get('href')  # URL-nı alırıq
    channel_list.append({
        'name': name,
        'url': url
    })

# JSON faylını yazırıq
output_path = os.path.join(os.getcwd(), 'channels.json')
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(channel_list, file, ensure_ascii=False, indent=4)

print(f'JSON faylı yaradıldı: {output_path}')
