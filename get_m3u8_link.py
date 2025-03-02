from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# ChromeDriver üçün Service təyin etmək
service = Service(ChromeDriverManager().install())  # avtomatik ChromeDriver versiyasını tapır
driver = webdriver.Chrome(service=service)

# Hədəf URL-i açın
driver.get('https://www.ecanlitvizle.app/xezer-tv-canli-izle/')  # burada URL dəyişə bilər

# Səhifənin yüklənməsini gözləyin
time.sleep(5)

# M3U8 linkini tapın və ekrana çap edin
try:
    m3u8_link = driver.find_element(By.XPATH, '//a[contains(@href, "m3u8")]').get_attribute('href')
    print(f"M3U8 Link: {m3u8_link}")
    
    # Linki bir TXT faylına yazın
    with open("m3u8_link.txt", "w") as f:
        f.write(m3u8_link)
    
except Exception as e:
    print(f"Xəta baş verdi: {str(e)}")

# ChromeDriver-ı bağlayın
driver.quit()
