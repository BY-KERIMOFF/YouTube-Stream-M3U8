from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Chrome driverni yükləyin və başlatın
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Headless modda işləyir
service = Service("/usr/bin/chromedriver")  # GitHub Actions-də chromedriver yolunu daxil edin
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Səhifəyə keçid edin
    driver.get("https://www.ecanlitvizle.app/azad-tv-azeri-izle-canli-1/")
    time.sleep(5)  # Səhifə yüklənməsinə gözləyin

    # Tokeni DOM-dan əldə edin
    token_element = driver.execute_script("return localStorage.getItem('token') || sessionStorage.getItem('token')")
    if not token_element:
        token_element = driver.find_element(By.XPATH, "//script[contains(., 'token')]").text

    print(f"Token: {token_element}")

    # Tokeni faylə yazın
    with open("token.txt", "w") as file:
        file.write(token_element)

finally:
    driver.quit()  # Browseri bağlayın
