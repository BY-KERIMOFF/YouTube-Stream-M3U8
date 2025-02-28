import requests
from bs4 import BeautifulSoup

def update_token():
    # Səhifə URL-i
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    
    # Səhifəni açırıq
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Səhifə açılmadı!")
        return
    
    # HTML-i BeautifulSoup ilə analiz edirik
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Token-i tapmaq üçün müvafiq elementi tapırıq
    token = None
    
    # İlk olaraq input elementində tokeni axtarırıq
    try:
        token = soup.find('input', {'name': 'token'})['value']
    except TypeError:
        print("Input elementində token tapılmadı!")
    
    # Əgər token tapılmadısa, meta tag-da tokeni yoxlayaq
    if not token:
        try:
            token = soup.find('meta', {'name': 'token'})['content']
        except TypeError:
            print("Meta tag-da token tapılmadı!")
    
    if not token:
        print("Token tapılmadı!")
        return

    # Yeni token ilə URL yaratmaq
    new_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740712041"
    print(f"Yeni URL: {new_url}")

# Skripti işə salmaq
if __name__ == "__main__":
    update_token()
