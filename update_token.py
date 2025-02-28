from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def update_token():
    # Chrome üçün başsız rejim əlavə et
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # ChromeDriver ilə əlaqə qur
    driver = webdriver.Chrome(options=chrome_options)
    
    # URL-ni aç
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)

    # Burada tokeni almaq və yeniləmək üçün lazımi kodu əlavə edin
    # Misal üçün, yeni tokeni alıb istifadə edə bilərsiniz

    time.sleep(5)  # Sayfanın yüklənməsi üçün gözləyirik

    # Yeni tokeni çəkin və işləminizi tamamlayın
    # driver.find_element_by_id("element_id") və ya digər metodlarla tokeni götürə bilərsiniz.

    print("Token başarıyla alındı!")

    # Web driver-ı bağlayın
    driver.quit()

if __name__ == "__main__":
    update_token()
