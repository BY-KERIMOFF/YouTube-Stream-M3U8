from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# WebDriver-i işə salmaq üçün Service və Options istifadə edirik
def get_new_token():
    # WebDriver üçün lazım olan xidmətin qurulması
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # GUI olmadan işləmək üçün
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # ChromeDriver-ın yolunu göstəririk
    service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')

    # WebDriver-i başlatmaq
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Tokeni əldə etmək üçün səhifə URL-ni daxil edirik
    driver.get("https://example.com")  # Tokeni aldığınız saytın URL-i

    try:
        # Token elementinin mövcudluğunu gözləyirik (10 saniyə gözləyəcək)
        token_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='token']"))
        )
        token = token_element.text
    except:
        print("Token tapılmadı!")
        driver.quit()
        return None

    driver.quit()  # WebDriver-u bağlayırıq

    return token

# Yeni tokeni alırıq
new_token = get_new_token()

if new_token:
    # Yeni tokenlə linki yaradıb çıxarırıq
    link = f"https://ecanlitv3.etvserver.com/tv8.m3u8?tkn={new_token}&tms=1740695213"
    print(f"Yeni link: {link}")
