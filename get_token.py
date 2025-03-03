import requests
from bs4 import BeautifulSoup

# Tokeni olan URL
token_url = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=b4zwWRWXY_x8qGQWPP7lWw&tms=1740967578"

# Token alınacaq səhifə
page_url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Başlıqlar
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# AJAX sorğusunu edirik
try:
    # İlk olaraq səhifəni alırıq
    page_response = requests.get(page_url, headers=headers)
    if page_response.status_code == 200:
        print("Səhifə uğurla alındı.")

        # BeautifulSoup ilə səhifə məzmununu təhlil edirik
        soup = BeautifulSoup(page_response.content, 'html.parser')

        # Buradan JavaScript kodlarını və ya AJAX sorğusunu tapmalıyıq
        # Misal olaraq, tokeni tapmaq üçün birbaşa HTML daxilində axtarış edirik.
        token = None
        for script in soup.find_all('script'):
            if 'token' in script.text:
                # JavaScript içindəki tokeni çıxartmaq
                start_index = script.text.find('token=') + len('token=')
                end_index = script.text.find('"', start_index)
                token = script.text[start_index:end_index]
                break

        if token:
            print("Yeni Token tapıldı:", token)
        else:
            print("Token tapılmadı, səhifə içində JavaScript kodunu araşdırın.")
    else:
        print(f"Səhifə alınmadı. HTTP Status Code: {page_response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Şəbəkə problemi oldu: {e}")
