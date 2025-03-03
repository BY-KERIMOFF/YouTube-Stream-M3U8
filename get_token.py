import requests
import re

def get_token():
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("❌ Səhifə açıla bilmədi!")
        return None
    
    # Saytın HTML mətnini çap et, problemi görməyə kömək edəcək
    print(response.text)
    
    # Tokeni tapmaq üçün regex istifadə edirik
    match = re.search(r'tkn=([a-zA-Z0-9_-]+)', response.text)
    if match:
        return match.group(1)
    
    print("❌ Token tapılmadı!")
    return None

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Token tapıldı: {token}")
    else:
        print("Token tapılmadı.")
