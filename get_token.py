import requests
import re

def get_token():
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("❌ Səhifə açıla bilmədi!")
        return None
    
    # Tokeni tapmaq
    match = re.search(r'tkn=([a-zA-Z0-9_-]+)', response.text)
    if match:
        return match.group(1)
    
    print("❌ Token tapılmadı!")
    return None

def update_stream_link(new_token):
    try:
        with open("stream_link.txt", "r") as file:
            content = file.read()
        
        # Köhnə tokeni tapıb onu yenisi ilə əvəz edirik
        updated_content = re.sub(r'tkn=[a-zA-Z0-9_-]+', f'tkn={new_token}', content)
        
        if content != updated_content:  # Əgər dəyişiklik olubsa
            with open("stream_link.txt", "w") as file:
                file.write(updated_content)
            print("✅ Token yeniləndi və stream_link.txt faylı güncəlləndi.")
        else:
            print("❌ Token dəyişməyib.")
    
    except FileNotFoundError:
        print("❌ stream_link.txt faylı tapılmadı!")
        return

if __name__ == "__main__":
    token = get_token()
    if token:
        update_stream_link(token)
