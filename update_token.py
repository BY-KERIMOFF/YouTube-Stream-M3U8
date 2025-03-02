import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Chrome üçün Selenium konfiqurasiyası
chrome_driver_path = "/path/to/chromedriver"  # Burada chromedriver yolunu düzgün daxil et

options = Options()
options.headless = True  # Görünməz rejimdə işləsin
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Sayta daxil ol
url = "https://www.ecanlitvizle.app/kucukcekmece-mobese-canli-izle/"
driver.get(url)
time.sleep(5)  # Saytın tam yüklənməsini gözlə

# Saytın HTML kodunu al
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")

# Tokeni HTML kodundan çıxar (Əgər HTML-dədirsə)
token_pattern = r'tkn=([a-zA-Z0-9]+)'
token_match = re.search(token_pattern, page_source)

if token_match:
    token = token_match.group(1)
    print(f"🔹 Token tapıldı: {token}")

else:
    print("❌ Token HTML-də tapılmadı, AJAX sorğusu yoxlanılır...")

    # AJAX sorğusu ilə tokeni əldə etməyə cəhd et
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    try:
        ajax_url = "https://www.ecanlitvizle.app/api/get_token"  # Xətaya görə Developer Tools-da URL-ni yoxla
        response = requests.get(ajax_url, headers=headers)

        if response.status_code == 200:
            token_match = re.search(token_pattern, response.text)
            if token_match:
                token = token_match.group(1)
                print(f"🔹 AJAX Token tapıldı: {token}")
            else:
                print("❌ AJAX sorğusunda da token tapılmadı.")
                token = None
        else:
            print(f"❌ AJAX sorğusu uğursuz oldu! Kod: {response.status_code}")
            token = None

    except Exception as e:
        print(f"⚠️ AJAX sorğusu zamanı xəta baş verdi: {e}")
        token = None

# Brauzeri bağla
driver.quit()

# Token tapılıbsa, işlək M3U8 linkini qur
if token:
    m3u8_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740960002"
    
    # Linki fayla yaz
    with open("tv.txt", "w") as file:
        file.write(m3u8_url)
    
    print(f"✅ Yeni M3U8 Linki: {m3u8_url}")
    print("✅ Link tv.txt faylına yazıldı!")

else:
    print("❌ Token tapılmadı, link yenilənmədi.")
