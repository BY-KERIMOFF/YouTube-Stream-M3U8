import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_token():
    # Set up the WebDriver
    options = Options()
    options.add_argument('--headless')  # Başsız rejimdə işləyir
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the page
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    # Wait for page to load and find the token
    time.sleep(5)  # Wait 5 seconds to ensure page is loaded, adjust if needed
    
    try:
        # Searching for the token in the page source
        token = driver.find_element(By.XPATH, "//script[contains(text(),'tkn=')]").get_attribute("innerHTML")
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
