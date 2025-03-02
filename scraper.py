import requests
from bs4 import BeautifulSoup
import os

# Sayta sorğu göndəririk
url = 'https://www.ecanlitvizle.app'
response = requests.get(url)
html = response.text

# BeautifulSoup ilə HTML-i analiz edirik
soup = BeautifulSoup(html, 'html.parser')

# Kanal linklərini tapırıq (XPath ilə deyil, CSS selector ilə)
channels = soup.find_all('a', class_='channel-link')  # Bu sinifi təhlil etməli olacaqsınız

# Faylın tam yolunu göstəririk
output_path = os.path.join(os.getcwd(), 'channels.m3u')

# M3U faylını yazırıq
with open(output_path, 'w') as file:
    file.write('#EXTM3U\n')  # M3U başlığı
    for channel in channels:
        name = channel.text.strip()
        url = channel.get('href')  # URL-nı alırıq
        file.write(f'#EXTINF:-1,{name}\n')
        file.write(f'{url}\n')

print(f'M3U faylı yaradıldı: {output_path}')
