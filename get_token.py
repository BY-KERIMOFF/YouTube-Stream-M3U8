from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. Chrome binary və chromedriver quraşdırılması
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 2. WebDriver Manager istifadə edərək `chromedriver`-i yükləyirik
driver_path = ChromeDriverManager().install()

# 3. WebDriver ilə Chrome-u işə salırıq
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 4. M3U8 linkində tokeni tapmaq
def get_new_token():
    driver.get("https://str.yodacdn.net/ictimai/tracks-v1a1/mono.ts.m3u8?token=39546e619c1c1afe6826bbea78fcd7dbcc8e97d0-11c9b759a05a4132917de2f36f267b2a-1740704082-1740693282")
    time.sleep(5)  # Sayfa yüklənsin

    # Tokeni tapırıq
    token_element = driver.find_element_by_xpath("//div[@id='token']")
    token = token_element.text
    return token

# 5. Tokeni alırıq
token = get_new_token()
print(f"Alınan token: {token}")

# 6. Chrome browserını bağlayırıq
driver.quit()
