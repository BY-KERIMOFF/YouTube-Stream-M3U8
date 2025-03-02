from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Selenium WebDriver setup
driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # ChromeDriver'ı müvafiq yol ilə dəyiş
driver.get('https://www.ecanlitvizle.app/xezer-tv-canli-izle/')

# Sayfanın yüklənməsini gözləyin
time.sleep(5)  # Sayfa tam yüklənməyibsə gözləyin

# M3U8 linkini tapın
m3u8_link = driver.find_element(By.XPATH, '//a[contains(@href, "m3u8")]').get_attribute('href')

print(f"M3U8 Link: {m3u8_link}")

driver.quit()
