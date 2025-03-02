from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Browser ayarları
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Başsız rejim
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Webdriver başlat
browser = webdriver.Chrome(options=options)

# Saytı aç
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
browser.get(url)

time.sleep(5)  # Elementlərin yüklənməsini gözləyək

# Tokenli linki tap
try:
    video_element = browser.find_element(By.TAG_NAME, "iframe")
    token_link = video_element.get_attribute("src")
    
    if token_link:
        print("Tokenli link tapıldı:", token_link)
        
        # Fayla yaz
        with open("token_link.txt", "w") as file:
            file.write(token_link)
    else:
        print("Tokenli link tapılmadı!")

except Exception as e:
    print("Xəta baş verdi:", e)

# Brauzeri bağla
browser.quit()
