import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# ChromeOptions konfiqurasiyası
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")  # Sandboxing-i deaktiv et
chrome_options.add_argument("--disable-dev-shm-usage")  # DevTools Active Port problemi üçün

# Chrome sürücüsünü yükləmək üçün webdriver-manager istifadə et
service = Service(ChromeDriverManager().install())

# WebDriver başlatmaq
driver = webdriver.Chrome(service=service, options=chrome_options)

# Web səhifəsini açmaq
driver.get("https://example.com")

# Sayfadan məlumatı alırıq (misal üçün)
channels = driver.find_elements(By.XPATH, "//a[contains(@href, '.m3u8')]")

# Faylın yaradılması
file_path = "channels.m3u"
with open(file_path, 'w') as f:
    f.write("# Example Channel M3U Content\n")
    for channel in channels:
        f.write(f"{channel.get_attribute('href')}\n")

# Faylın mövcudluğunu yoxlayaq
if os.path.exists(file_path):
    print(f"{file_path} yaradıldı!")
else:
    print(f"{file_path} tapılmadı!")

# Chrome sürücüsünü bağlayırıq
driver.quit()
