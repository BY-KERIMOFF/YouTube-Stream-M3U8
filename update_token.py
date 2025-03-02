import requests
from bs4 import BeautifulSoup
import re

# Sayt URL-i
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Saytın HTML məzmununu əldə edirik
response = requests.get(url)

# HTML məzmununu BeautifulSoup ilə parse edirik
soup = BeautifulSoup(response.text, "html.parser")

# Tokeni regex ilə tapırıq
match = re.search(r'tkn=([a-zA-Z0-9]+)', soup.prettify())
if match:
    new_token = match.group(1)
    print(f"Yeni token tapıldı: {new_token}")
else:
    print("Yeni token tapılmadı.")
    exit()

# Əsas URL-i yeniləyirik
old_url = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=NEW_TOKEN_HERE&tms=1740960002"
new_url = old_url.replace("NEW_TOKEN_HERE", new_token)

print(f"Yeni URL: {new_url}")

# tv.txt faylını oxuyuruq və yeni linki yazırıq
try:
    with open('tv.txt', 'r') as file:
        content = file.read()
        print("Faylın əvvəlki məzmunu:")
        print(content)
except FileNotFoundError:
    print("tv.txt faylı tapılmadı.")
    exit()

# Yenilənmiş məzmunu tv.txt faylında saxlayırıq
with open('tv.txt', 'w') as file:
    file.write(new_url)

print("Yeni link tv.txt faylında yazıldı!")
