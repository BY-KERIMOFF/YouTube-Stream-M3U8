# update_token.py
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def update_token():
    # M3U8 linki alın
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/?anahtar=YOUR_TOKEN_HERE"
    
    # Selenium ilə səhifəni açmaq
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Başsız işlətmək üçün
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    # Tokeni dəyişdir
    new_token = "new_generated_token"
    updated_url = url.replace("YOUR_TOKEN_HERE", new_token)
    
    print("Updated URL:", updated_url)
    driver.quit()

if __name__ == "__main__":
    update_token()
