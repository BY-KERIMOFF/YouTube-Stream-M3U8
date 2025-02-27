import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from selenium.webdriver.common.action_chains import ActionChains

# .env faylını yükləyirik
load_dotenv()

# URL və digər parametrləri oxuyuruq
M3U_TOKEN_URL = os.getenv("M3U_TOKEN_URL")

# GitHub parametrləri
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
REPO_NAME = os.getenv("REPO_NAME")

# Chrome parametrləri
chrome_options = Options()
chrome_options.add_argument("--headless")  # Gizli rejimdə işləməyi təmin edirik
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Chrome xidmətini yaratmaq
service = Service('/usr/lib/chromium-browser/chromedriver')

# Yeni token əldə etmək üçün funksiya
def get_new_token():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        # İstədiyiniz səhifəni açın
        driver.get(M3U_TOKEN_URL)
        
        # Səhifə yüklənməsini gözləyirik
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='token']"))  # Tokenin olduğu elementi gözləyirik
        )

        # Tokeni tapırıq
        token_element = driver.find_element(By.XPATH, "//div[@id='token']")
        token = token_element.text
        return token
    except Exception as e:
        print(f"Token tapılmadı: {str(e)}")
        return None
    finally:
        driver.quit()

# M3U faylını yeniləmək
def update_m3u(token):
    m3u_content = f"#EXTM3U\n#EXTINF:-1,İctimai TV\n{M3U_TOKEN_URL}?token={token}"
    with open("token.m3u8", "w") as file:
        file.write(m3u_content)
    print("M3U faylı yeniləndi!")

# GitHub-a yükləmək üçün funksiya
def upload_to_github():
    # GitHub API vasitəsilə faylı yükləmək üçün URL
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/token.m3u8"
    
    # Faylın məzmununu oxuyuruq
    with open("token.m3u8", "r") as file:
        content = file.read()

    # GitHub-a yükləmək üçün payload
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "message": "M3U faylı yeniləndi",
        "content": content.encode("utf-8").decode("utf-8")  # Base64 formatında göndəririk
    }

    response = requests.put(api_url, json=data, headers=headers)
    if response.status_code == 201:
        print("Fayl GitHub-a uğurla yükləndi!")
    else:
        print(f"Xəta baş verdi: {response.status_code}, {response.text}")

# Əsas işə salma
if __name__ == "__main__":
    try:
        while True:
            new_token = get_new_token()
            if new_token:
                update_m3u(new_token)
                upload_to_github()
            time.sleep(3600)  # Hər 1 saatda bir yeniləyirik
    except KeyboardInterrupt:
        print("Proses dayandırıldı.")
