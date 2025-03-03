import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_token_from_page(url):
    """URL-ə gedir və tokeni alır"""
    options = Options()
    options.add_argument('--headless')  # Başsız rejimdə işləyir
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL-i açır
    driver.get(url)
    
    try:
        # Sayfa tam yükləndikdən sonra tokeni tapmaq
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//script[contains(text(),'tkn=')]"))
        )

        # Tokenin olduğu script elementini tapırıq
        script = driver.find_element(By.XPATH, "//script[contains(text(),'tkn=')]")
        token = script.get_attribute("innerHTML")
        token = token.split("tkn=")[1].split("'")[0]
        driver.quit()
        return token
    except Exception as e:
        print(f"❌ Token tapılmadı! Error: {e}")
        driver.quit()
        return None

def save_token_to_file(token, filename="token.txt"):
    """Tokeni fayla yazır"""
    try:
        with open(filename, "w") as file:
            file.write(token)
        print(f"✅ Yeni token {filename} faylına yazıldı.")
    except Exception as e:
        print(f"❌ Token fayla yazılarkən xəta baş verdi: {e}")

if __name__ == "__main__":
    # URL-dən tokeni alırıq
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"  # Hedef URL

    print(f"✅ {url} üçün token alınıb:")
    token = get_token_from_page(url)
    
    if token:
        # Tokeni faylda saxlayırıq
        save_token_to_file(token)
    else:
        print("❌ Token tapılmadı!")
