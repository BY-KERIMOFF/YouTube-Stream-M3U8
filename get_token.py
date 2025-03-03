import re
import requests

# URL daxil edin
url = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=JCm4CeptUoCkaoqwLPifNQ&tms=1740967951"

# URL-dən tokeni çıxarmaq
token_match = re.search(r'tkn=([A-Za-z0-9-_]+)', url)
if token_match:
    token = token_match.group(1)
    print(f"Token tapıldı: {token}")
else:
    print("Token tapılmadı!")

# Tokeni istifadə edərək sorğu göndərmək
response = requests.get(url)
if response.status_code == 200:
    print("Sorğu uğurla yerinə yetirildi!")
else:
    print(f"Error: {response.status_code}")
