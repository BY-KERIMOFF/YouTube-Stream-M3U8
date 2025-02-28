from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Chrome-u başsız rejimdə işə salmaq üçün parametrlər
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# WebDriver Manager ilə `chromedriver`-i yükləmək
driver_path = ChromeDriverManager().install()

# WebDriver ilə Chrome-u işə salırıq
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Tokeni alma funksiyası
def get_new_token():
    driver.get("https://live.cdn-canlitv.com/aztv2.m3u8?anahtar=QEoJcC_5a3IVTERXetIwJg&sure=1740723511&ip=185.146.115.168")
    time.sleep(5)  # Sayfanın yüklənməsini gözləyirik

    # Tokeni tapırıq
    token_element = driver.find_element(By.XPATH, "//div[@id='token']")
    token = token_element.text
    return token

# Tokeni alırıq və çap edirik
token = get_new_token()
print(f"Alınan token: {token}")

# Chrome browserını bağlayırıq
driver.quit()
