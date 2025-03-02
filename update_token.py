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
        
        # Yeni tokeni tap (bu addımda, sənin saytında necə token əldə edildiyini göstərən kod əlavə etməlisiniz)
        new_token = "NEW_TOKEN_HERE"  # Burada yeni tokeni əldə etməli və onu istifadə etməlisiniz
        new_link = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={new_token}&tms=1740960002"
        print(f"Yeni link: {new_link}")

        # Faylı yaz (hər halda yazacaq)
        with open("tv.txt", "w") as f:
            f.write(new_link)
        print("Yeni link tv.txt faylında yazıldı!")
    else:
        print("Köhnə token tapılmadı.")
        # Əgər heç bir token tapılmasa da, tv.txt faylını yenilə
        with open("tv.txt", "w") as f:
            f.write("No token found!")
        print("Heç bir token tapılmadı, boş məlumat tv.txt faylında saxlanıldı.")
else:
    print("Saytla əlaqə qurulmadı.")
    with open("tv.txt", "w") as f:
        f.write("Failed to fetch URL")
    print("Saytla əlaqə qurulmadı, səhv mesajı tv.txt faylında saxlanıldı.")
