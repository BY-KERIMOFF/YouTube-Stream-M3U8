from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Browser ayarları
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Başsız rejim
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")  # Uzantıları bağlamaq

# ChromeDriver yolunu əlinizlə təyin edin
chrome_driver_path = "/path/to/chromedriver"  # Burada öz yolunuzu yazın
browser = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

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
