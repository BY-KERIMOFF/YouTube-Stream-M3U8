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
match = re.search(r'tkn=([A-Za-z0-9_-]+)', soup.text)

if match:
    token = match.group(1)
    print(f"✅ Yeni token: {token}")
    with open("token.txt", "w") as f:
        f.write(token)
else:
    print("❌ Token tapılmadı!")
    # Token tapılmadıqda yeni bir link əlavə edirik
    with open("token.txt", "w") as f:
        f.write("new_token_placeholder")  # Yeni linkin tokenini buraya əlavə edə bilərsiniz
