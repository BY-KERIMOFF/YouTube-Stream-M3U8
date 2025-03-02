import re
import requests

# Yeni tokeni əldə etmək üçün URL
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# tv.txt faylını oxumaq
with open('tv.txt', 'r') as file:
    content = file.read()

# Köhnə tokeni tapmaq üçün regular expression istifadə edirik
match = re.search(r'tkn=([a-zA-Z0-9]+)', content)

if match:
    old_token = match.group(1)
    print(f"Köhnə token tapıldı: {old_token}")
    
    # Yeni tokeni əldə etmək üçün URL-i sorğu edirik
    response = requests.get(url)
    
    # Burada, yeni tokeni müvafiq yerdən götürmək lazımdır. Misal üçün:
    # Yeni tokenin HTML səhifəsindən əldə edilməsi
    new_token = "NEW_TOKEN_HERE"  # Burada 'NEW_TOKEN_HERE' ilə yeni tokeni əvəz edin.

    # Köhnə tokeni yeni token ilə dəyişdiririk
    new_content = content.replace(f'tkn={old_token}', f'tkn={new_token}')
    
    # Yeni linki və yeni tokeni ekrana yazdırmaq
    print(f"Yeni token: {new_token}")
    print(f"Yeni link: {new_content.splitlines()[0]}")  # İlk sətirdə link varsa

    # tv.txt faylını yenidən yazmaq
    with open('tv.txt', 'w') as file:
        file.write(new_content)
    
    print("Yeni link tv.txt faylında yazıldı!")
else:
    print("Köhnə token tapılmadı.")
