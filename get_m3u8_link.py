import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ChromeDriver versiyasını düzgün təyin edin (məsələn, 113.0.5672.63)
service = Service(ChromeDriverManager(version="113.0.5672.63").install())  # Uyğun versiyanı təyin et
driver = webdriver.Chrome(service=service)

# URL-i açın
driver.get('https://www.ecanlitvizle.app/xezer-tv-canli-izle/')

# Səhifənin tam yüklənməsini gözləyin
time.sleep(5)

# M3U8 linkini tapın və ekrana çap edin
try:
    m3u8_link = driver.find_element(By.XPATH, '//a[contains(@href, "m3u8")]').get_attribute('href')
    print(f"M3U8 Link: {m3u8_link}")

    # Linki bir txt faylında qeyd edin
    with open('m3u8_link.txt', 'w') as file:
        file.write(m3u8_link)
except Exception as e:
    print(f"Xəta baş verdi: {e}")
finally:
    driver.quit()  # Browserı bağla
