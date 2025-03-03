import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_token():
    # Set up the WebDriver
    options = Options()
    options.add_argument('--headless')  # Başsız rejimdə işləyir
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the page
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    try:
        # Gözləmə tətbiq et, səhifənin tam yüklənməsini təmin et
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//script[contains(text(),'tkn=')]"))
        )
        
        # Token-in olduğu script elementini tap
        script = driver.find_element(By.XPATH, "//script[contains(text(),'tkn=')]")
        token = script.get_attribute("innerHTML")
        token = token.split("tkn=")[1].split("'")[0]
        driver.quit()
        return token
    except Exception as e:
        print(f"❌ Token tapılmadı! {e}")
        driver.quit()
        return None

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Token: {token}")
    else:
        print("❌ Token tapılmadı!")
