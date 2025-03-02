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

# Köhnə tokeni və yeni tokeni faylda əvəz edirik
old_token = "Fh2F2HhcbuZaxDX8hYPQqQ"  # Köhnə tokeni burada yazın

# tv.txt faylını oxuyuruq və köhnə token ilə yeni tokeni əvəz edirik
with open('tv.txt', 'r') as file:
    content = file.read()

# Tokeni dəyişdiririk
content = content.replace(old_token, new_token)

# Yenilənmiş məzmunu faylda saxlayırıq
with open('tv.txt', 'w') as file:
    file.write(content)

print("Yeni token tv.txt faylında yazıldı!")
