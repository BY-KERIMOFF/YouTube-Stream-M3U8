from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Chrome üçün konfigurasiya
chrome_options = Options()
chrome_options.add_argument("--headless")  # Görsəl interfeys olmadan işləsin
chrome_options.add_argument("--no-sandbox")  # Sandbox-u deaktiv et
chrome_options.add_argument("--disable-dev-shm-usage")  # Dev-shm istifadəsini deaktiv et
chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging portu

# ChromeDriver yolu
chrome_driver_path = "/usr/local/bin/chromedriver"

# ChromeService-i başlatmaq
service = Service(chrome_driver_path)

# WebDriver-i başlatmaq
driver = webdriver.Chrome(service=service, options=chrome_options)

# Scraping və digər əməliyyatlar
driver.get("https://www.ecanlitvizle.app/xezer-tv-canli-izle/")

# Əlavə əməliyyatlar (səhifəni oxuma, məlumat əldə etmə və s.)
# ...

# Skripti bitirmək
driver.quit()
