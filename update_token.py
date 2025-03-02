import re
import requests

# TV linkinin olduğu URL (sənə uyğun URL-ni burada istifadə et)
url = 'https://www.ecanlitvizle.app/xezer-tv-canli-izle/'

# Linkdən məlumatları al
response = requests.get(url)

# Əgər düzgün cavab alınarsa, tokeni tapmaq
if response.status_code == 200:
    html_content = response.text
    old_token_match = re.search(r'tkn=([A-Za-z0-9]+)', html_content)
    
    if old_token_match:
        old_token = old_token_match.group(1)
        print(f"Köhnə token tapıldı: {old_token}")
        
        # Yeni tokeni tap (bu addımda, sənin saytında necə token əldə edildiyini göstərən kod əlavə etməlisən)
        new_token = "NEW_TOKEN_HERE"  # Burada yeni tokeni əldə etməli və onu istifadə etməlisiniz
        new_link = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={new_token}&tms=1740960002"
        print(f"Yeni link: {new_link}")

        # Faylı yaz
        with open("tv.txt", "w") as f:
            f.write(new_link)
        print("Yeni link tv.txt faylında yazıldı!")
    else:
        print("Köhnə token tapılmadı.")
else:
    print("Saytla əlaqə qurulmadı.")
