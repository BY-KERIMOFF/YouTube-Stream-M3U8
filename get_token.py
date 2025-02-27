import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_new_token(youtube_url):
    # Chrome üçün başsız (headless) rejim qururuq
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # GUI olmadan işləmək üçün
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # WebDriver konfiqurasiyası
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # YouTube canlı yayınının URL-sini açırıq
    driver.get(youtube_url)

    # Tokeni tapmağa çalışırıq
    try:
        # Token elementini tapmağa çalışırıq
        token_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='token']"))
        )
        token = token_element.text
        print(f"Yeni token: {token}")
        return token
    except Exception as e:
        print(f"Token tapılmadı! Xəta: {e}")
        driver.quit()
        return None

    driver.quit()

if __name__ == "__main__":
    # YouTube kanalının canlı yayın linkini əlavə edin
    youtube_url = "https://www.youtube.com/watch?v=ouuCjEjyKVI"  # Burada kanalın canlı yayın linkini dəyişin

    new_token = get_new_token(youtube_url)

    if new_token:
        # Tokeni fayla yazırıq
        with open('token.m3u8', 'w') as f:
            f.write(f'#EXTM3U\n#EXTINF:0, YouTube Canlı Yayın\n{new_token}\n')

        print("Yeni M3U faylı yaradıldı: token.m3u8")
