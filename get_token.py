import requests
from bs4 import BeautifulSoup
import re

# Sayt URL-si
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Saytı əldə edirik
response = requests.get(url)

# Saytın HTML məzmununu parse edirik
soup = BeautifulSoup(response.text, 'html.parser')

# Saytdan tokeni tapmağa çalışırıq
# HTML-də tkn= dəyərini tapmağa çalışırıq
match = re.search(r'tkn=([A-Za-z0-9_-]+)', soup.text)

if match:
    token = match.group(1)
    print(f"Yeni token: {token}")
else:
    print("Token tapılmadı!")
