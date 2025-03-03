import requests
import re
import os

def get_token():
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("❌ Səhifə açıla bilmədi!")
        return None
    
    match = re.search(r'tkn=([a-zA-Z0-9_-]+)', response.text)
    if match:
        return match.group(1)
    
    print("❌ Token tapılmadı!")
    return None

def save_m3u8(token):
    base_m3u8_url = "https://ecanlitv3.etvserver.com/xazartv.m3u8"
    full_m3u8_url = f"{base_m3u8_url}?tkn={token}&tms=1740967951"
    
    m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=300000
{full_m3u8_url}
"""
    
    with open("stream.m3u8", "w") as file:
        file.write(m3u8_content)
    
    print("✅ Yeni M3U8 faylı yaradıldı: stream.m3u8")

def commit_and_push():
    os.system("git config --global user.name 'github-actions'")
    os.system("git config --global user.email 'github-actions@github.com'")
    os.system("git add stream.m3u8")
    os.system("git commit -m 'Yeni token ilə M3U8 faylı yeniləndi'")
    os.system("git push")

if __name__ == "__main__":
    token = get_token()
    if token:
        save_m3u8(token)
        commit_and_push()
