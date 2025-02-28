from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# WebDriver ayarları
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Başlıq olmadan işləmək
driver = webdriver.Chrome(options=options)

# Tokenin olduğu səhifə URL-si
url = "SƏHİFƏ_URL"  # Tokeni tapacağın səhifənin URL-si

# Səhifəni aç
driver.get(url)

# Tokeni tapmaq üçün XPath ilə elementə çatmaq
token_element = driver.find_element(By.XPATH, 'TOKEN_ELEMENT_XPATH')  # XPath yerinə doğru elementi yazmalısan
token = token_element.get_attribute("value")  # Əgər token bir input sahəsindədirsə

# Tokeni çap et (və ya istifadə et)
print(token)

# Bağlantını bağla
driver.quit()

# M3U8 linkini yeniləyək
m3u8_url = f"https://live.cdn-canlitv.com/aztv2.m3u8?anahtar={token}&sure"

# M3U8 faylını aç və yeni linki yaz
with open("aztv2.m3u8", "w") as file:
    file.write(m3u8_url)  # Yeni M3U8 URL-sini fayla yaz
