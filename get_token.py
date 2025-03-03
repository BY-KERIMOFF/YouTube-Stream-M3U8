import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim (GUI olmadan çalışır)

# WebDriver üçün Service yaratmaq
service = Service(ChromeDriverManager().install())

# WebDriver-i başlatmaq
driver = webdriver.Chrome(service=service, options=chrome_options)

# Hedef URL
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Saytı açırıq
driver.get(url)

# Sayta tam yüklənməsini gözləyirik
time.sleep(5)

# Tokeni tapmağa çalışırıq
token_element = None
token = None
try:
    token_element = driver.find_element("xpath", "//script[contains(text(),'tkn=')]")  # Yeni metod istifadə edilir
    token_script = token_element.get_attribute('innerHTML')
    start_index = token_script.find("tkn=") + 4
    end_index = token_script.find("&", start_index)
    token = token_script[start_index:end_index] if end_index != -1 else token_script[start_index:]
    print(f"Token tapıldı: {token}")

    # Tokeni faylda saxlamaq
    with open("token.txt", "w") as f:
        f.write(token)
    print("✅ Token fayla yazıldı.")
except Exception as e:
    print(f"❌ Token tapılmadı! Error: {e}")

# Əgər token tapılmadısa, köhnə stream.m3u8 faylını sil və yeni link əlavə et
if not token:
    if os.path.exists("stream.m3u8"):
        os.remove("stream.m3u8")  # Köhnə faylı silirik
    # Yeni linki əlavə edirik
    new_link = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=new_token&tms=1740969806"
    with open("stream.m3u8", "w") as f:
        f.write(new_link)
    print("✅ Köhnə token tapılmadı. Yeni tokenlə stream.m3u8 faylı yeniləndi.")
else:
    # Token tapılarsa stream.m3u8 faylını yeniləyirik
    new_m3u8_link = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740969806"
    with open("stream.m3u8", "w") as f:
        f.write(new_m3u8_link)
    print("✅ stream.m3u8 faylı yeniləndi.")

# Driver-i bağlayırıq
driver.quit()
