import requests
from bs4 import BeautifulSoup

# URL'yi daxil edirik
url = "https://www.ecanlitvizle.app/embed.php?kanal=xezer-tv-canli-izle"

# GET sorğusu göndəririk
response = requests.get(url)

# Sorğu uğurlu oldusa
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # HTML-də 'tkn=' olan script tagini tapırıq
    script_tag = soup.find('script', text=lambda t: t and 'tkn=' in t)
    if script_tag:
        # Tokeni çıxarırıq
        script_content = script_tag.string
        # Tokeni çəkmək üçün regex istifadə edə bilərik
        import re
        token = re.search(r'tkn=([^"]+)', script_content)
        if token:
            print(f"Token tapıldı: {token.group(1)}")
        else:
            print("Token tapılmadı")
    else:
        print("Token içeren script tapılmadı")
else:
    print("Sorğu uğursuz oldu")
