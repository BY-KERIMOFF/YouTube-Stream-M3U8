from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def update_token():
    options = Options()
    options.add_argument("--headless")  # GUI olmadan işləmək
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)

    # Burada səhifəni axtarış və tokeni əldə etmə əməliyyatlarını edirik
    print("Səhifəyə uğurla daxil oldu.")
    
    driver.quit()

if __name__ == "__main__":
    update_token()
