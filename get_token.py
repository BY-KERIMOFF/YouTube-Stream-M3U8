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

def update_token_in_file(new_token, filename="stream_link.txt"):
    """stream_link.txt faylında tokeni yeniləyir və ya yeni link əlavə edir"""
    try:
        # Faylı oxuyuruq
        try:
            with open(filename, "r") as file:
                content = file.read()
            
            # Köhnə token varsa, yenilə
            if 'tkn=' in content:
                old_token = content.split('tkn=')[1].split('&')[0]
                new_content = content.replace(old_token, new_token)
            else:
                new_content = content
        except FileNotFoundError:
            new_content = ""

        # Faylın sonuna yeni link əlavə edirik
        new_link = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={new_token}&tms={int(time.time())}\n"
        new_content += new_link

        # Faylı yenidən yazırıq
        with open(filename, "w") as file:
            file.write(new_content)
        print(f"✅ Token müvəffəqiyyətlə yeniləndi və ya yeni link əlavə olundu.")
    except Exception as e:
        print(f"❌ Tokeni faylda yeniləməkdə səhv: {e}")

if __name__ == "__main__":
    # URL-dən tokeni alırıq
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"  # Hedef URL

    print(f"✅ {url} üçün token alınıb:")
    token = get_token_from_page(url)
    
    if token:
        # Fayldakı tokeni yeniləyirik və ya yeni link əlavə edirik
        update_token_in_file(token)
    else:
        print("❌ Token tapılmadı!")
