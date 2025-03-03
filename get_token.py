import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Chrome sürücüsünü qururuq
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# WebDriver və səhifə açılır
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get("https://ecanlitv3.etvserver.com/xazartv.m3u8")

try:
    # Sayfa tam yükləndikdən sonra tokeni tapmaq üçün gözləyirik
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//script[contains(text(),'tkn=')]"))
    )

    # XPath ilə tokeni tapırıq
    token_script = driver.find_element(By.XPATH, "//script[contains(text(),'tkn=')]").get_attribute("innerHTML")
    
    # Tokeni çıxarırıq
    start_index = token_script.find('tkn=') + 4
    end_index = token_script.find('&', start_index)
    token = token_script[start_index:end_index] if end_index != -1 else token_script[start_index:]
    
    # Token tapılıbsa, fayla yazırıq
    if token:
        with open("token.txt", "w") as file:
            file.write(token)
        print("✅ Token tapıldı.")
    else:
        print("❌ Token tapılmadı!")

except Exception as e:
    print(f"❌ Hata baş verdi: {e}")
finally:
    driver.quit()
