import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Browser ayarları
options = Options()
options.add_argument("--headless")  # Başsız rejim
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")  # Uzantıları bağlamaq

# ChromeDriver versiyasını tapmaq və ya əl ilə yükləmək
try:
    # webdriver-manager istifadə edərək ChromeDriver versiyasını avtomatik yükləyin
    chrome_driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver path: {chrome_driver_path}")
except Exception as e:
    print("Webdriver-manager ilə ChromeDriver tapılmadı, əl ilə yükləyirik...")
    
    # Burada versiya uyğun olmayan ChromeDriver yükləmək üçün əl ilə yükləmə təlimatını yazın
    # Əgər versiyanız uyğun deyilsə, burada əl ilə yüklənmiş ChromeDriver-ı istifadə edə bilərsiniz
    chrome_driver_path = "/path/to/your/downloaded/chromedriver"  # Öz yolda dəyişdirin

# WebDriver başlat
service = Service(chrome_driver_path)
browser = webdriver.Chrome(service=service, options=options)

# Saytı aç
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
browser.get(url)

try:
    # Elementin yüklənməsini gözləyin (iframe tapılana qədər)
    video_element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    
    # Tokenli linki tap
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
finally:
    # Brauzeri bağla
    browser.quit()
