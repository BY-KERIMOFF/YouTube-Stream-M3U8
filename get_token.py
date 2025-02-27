from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# 1. Chrome binary və chromedriver quraşdırılması
chrome_binary_path = "/usr/bin/chromium-browser"  # Bu yol sizə uyğun olmalıdır
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = chrome_binary_path

# 2. `chromedriver`-in doğru yolunu göstəririk (GitHub Actions üçün əl ilə)
driver_path = "/usr/local/bin/chromedriver"  # `chromedriver` faylının tam yolu

# 3. WebDriver ilə Chrome-u işə salırıq
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 4. M3U8 linkində tokeni tapmaq
def get_new_token():
    driver.get("https://str.yodacdn.net/ictimai/tracks-v1a1/mono.ts.m3u8?token=e94ce96ed0bb56a38653e3258d32bddd4800a6be-866797cc0d6dbea82bcd1353aa390e56-1740700536-1740689736")
    time.sleep(5)  # Sayfa yüklənsin

    # Tokeni tapırıq
    token_element = driver.find_element(By.XPATH, "//div[@id='token']")
    token = token_element.text
    return token

# 5. Tokeni alırıq
token = get_new_token()
print(f"Alınan token: {token}")

# 6. Chrome browserını bağlayırıq
driver.quit()
