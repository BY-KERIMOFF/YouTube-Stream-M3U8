import requests
from bs4 import BeautifulSoup
import re

# Sayta sorğu göndəririk
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"  # Bu linkdə tokeni axtaracağıq
response = requests.get(url)

# Saytın HTML-i alırıq
soup = BeautifulSoup(response.text, "html.parser")

# Tokeni tapmaq üçün HTML-i yoxlayırıq
match = re.search(r'tkn=([a-zA-Z0-9]+)', soup.prettify())

if match:
    old_token = match.group(1)
    print(f"Köhnə token tapıldı: {old_token}")
else:
    print("Köhnə token tapılmadı.")
    exit()

# Yeni tokeni əldə et (bu müvəqqəti olaraq dəyişdirilə bilər)
new_token = "NEW_TOKEN_HERE"  # Yeni tokeni buraya daxil et

# URL-dəki köhnə tokeni yeni token ilə əvəz edirik
new_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={new_token}&tms=1740960002"

print(f"Yeni URL: {new_url}")

# Yeni linki tv.txt faylında yazırıq
with open('tv.txt', 'w') as file:
    file.write(new_url)

print("Yeni link tv.txt faylında yazıldı!")
