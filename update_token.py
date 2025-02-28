import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def update_token():
    # Verilən URL-ə daxil oluruq
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

    # Chrome sürücüsünü başlatmaq üçün opsiyalar
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Başsız rejimdə işlətmək
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    
    # Səhifəyə gedirik
    driver.get(url)

    # Səhifənin tam yüklənməsi üçün gözləyirik
    time.sleep(5)  # Vaxtı səhifənin yüklənmə sürətinə görə tənzimləyə bilərsiniz

    try:
        # Tokeni tapmaq üçün səhifədəki uyğun elementi tapmalıyıq
        # Bu XPath səhifənin strukturuna əsasən dəyişə bilər
        token_element = driver.find_element(By.XPATH, "//*[contains(text(), 'tkn=')]")
        token_url = token_element.get_attribute('href')  # Tokenin olduğu linki alırıq

        # Yeni tokeni URL-dən çıxarırıq
        new_token = token_url.split('tkn=')[1].split('&')[0]  # Tokeni ayırırıq
        print(f"Yeni token: {new_token}")

        # Yeni URL-ni qururuq
        new_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={new_token}&tms=1740712041"
        print("Yeni URL:", new_url)
    except Exception as e:
        print(f"Token tapılmadı: {e}")
    
    # Sürücüyü bağlayırıq
    driver.quit()

if __name__ == "__main__":
    update_token()
