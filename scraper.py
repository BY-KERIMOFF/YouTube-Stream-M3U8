import requests
from bs4 import BeautifulSoup
import os

# M3U linklərini tapmaq üçün URL-lər
urls = [
    "https://www.ecanlitvizle.app/xezer-tv-canli-izle/",
    "https://www.ecanlitvizle.app/show-tv-canli-izle-hd-4/",
    "https://www.ecanlitvizle.app/tlc-tv-canli/"
]

# Tapılan M3U linklərini saxlamaq üçün fayl
output_path = os.path.join(os.getcwd(), 'm3u_links.txt')

# M3U linklərini tapıb fayla yazmaq
with open(output_path, 'w', encoding='utf-8') as file:
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
                file.write(f'{href}\n')  # Tapılan M3U linkini fayla yazırıq

print(f'M3U linkləri {output_path} faylına yazıldı.')
