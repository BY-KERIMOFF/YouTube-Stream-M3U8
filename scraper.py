import requests
import re
from datetime import datetime

# Tokenli link
url = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=Fh2F2HhcbuZaxDX8hYPQqQ&tms=1740960002"

# Linkdəki tokeni tapmaq üçün regex istifadə edirik
def get_new_token(url):
    try:
        response = requests.get(url)
        # URL-dəki tokeni regex ilə çəkirik
        token_match = re.search(r'tkn=([A-Za-z0-9]+)', response.url)
        
        if token_match:
            return token_match.group(1)  # Yeni tokeni qaytarır
        else:
            print("Token tapılmadı.")
            return None
    except Exception as e:
        print(f"Xəta baş verdi: {e}")
        return None

# Yeni tokeni al
new_token = get_new_token(url)

if new_token:
    # Yeni tokeni faylda saxlamaq
    with open("new_token.txt", "w") as file:
        file.write(f"Yeni Token: {new_token}\n")
        file.write(f"Tarix: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"Yeni token {new_token} fayla yazıldı.")
else:
    print("Yeni token tapılmadı.")
