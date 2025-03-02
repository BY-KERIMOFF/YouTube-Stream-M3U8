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

# tv.txt faylını oxuyuruq
try:
    with open('tv.txt', 'r') as file:
        content = file.read()
        print("Faylın əvvəlki məzmunu:")
        print(content)
except FileNotFoundError:
    print("tv.txt faylı tapılmadı.")
    exit()

# Köhnə tokeni yeni token ilə əvəz edirik
old_token = "Fh2F2HhcbuZaxDX8hYPQqQ"
if old_token in content:
    content = content.replace(old_token, new_token)
    print(f"Köhnə token tapıldı: {old_token}")
    print(f"Yeni token: {new_token}")
else:
    print(f"Köhnə token tapılmadı: {old_token}")
    exit()

# Yenilənmiş məzmunu tv.txt faylında saxlayırıq
with open('tv.txt', 'w') as file:
    file.write(content)

print("Yeni token tv.txt faylında yazıldı!")
