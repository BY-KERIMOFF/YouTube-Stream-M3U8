from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Əgər Chrome versiyanı 133.0.6943 istifadə edirsinizsə, versiyanı belə təyin edin:
service = Service(ChromeDriverManager(version="133.0.6943").install())
driver = webdriver.Chrome(service=service)

driver.get('https://www.ecanlitvizle.app/xezer-tv-canli-izle/')

time.sleep(5)

# M3U8 linkini tapın
m3u8_link = driver.find_element(By.XPATH, '//a[contains(@href, "m3u8")]').get_attribute('href')

print(f"M3U8 Link: {m3u8_link}")

driver.quit()
