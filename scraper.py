from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Chrome driver yolunu birbaşa göstəririk
chrome_driver_path = "/usr/local/bin/chromedriver"  # Bu yola əmin olun

# Chrome-un başlatma seçimləri
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUI olmadan işlə

# Selenium-da Chrome sürücüsünü işə salırıq
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Scraper işini yerinə yetirən hissə
driver.get("https://www.ecanlitvizle.app/xezer-tv-canli-izle/")
time.sleep(5)  # Saytın yüklənməsi üçün zaman qoyuruq

# Hər hansı bir elementlə qarşılaşmaq
# Bu, kanalların M3U linklərini tapmaq üçün uyğun elementlərə daxil olmağı tələb edir
# Məsələn:
# m3u_link = driver.find_element(By.XPATH, 'xpath-of-m3u-link')

driver.quit()
