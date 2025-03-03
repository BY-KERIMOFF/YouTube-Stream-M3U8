from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim (GUI olmadan çalışır)

# Webdriver-i yükləyirik
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

# Hedef URL
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Saytı açırıq
driver.get(url)

# Sayta tam yüklənməsini gözləyirik
time.sleep(5)

# Tokeni tapmağa çalışırıq
token_element = None
try:
    token_element = driver.find_element_by_xpath("//script[contains(text(),'tkn=')]")
    token_script = token_element.get_attribute('innerHTML')
    start_index = token_script.find("tkn=") + 4
    end_index = token_script.find("&", start_index)
    token = token_script[start_index:end_index] if end_index != -1 else token_script[start_index:]
    print(f"Token tapıldı: {token}")

    # Tokeni faylda saxlamaq
    with open("token.txt", "w") as f:
        f.write(token)
    print("✅ Token fayla yazıldı.")
except Exception as e:
    print(f"❌ Token tapılmadı! Error: {e}")

# Driver-i bağlayırıq
driver.quit()
