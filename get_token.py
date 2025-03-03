import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ChromeDriver və Chrome'u başlatmaq
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless rejimi (brauzersiz)

# ChromeDriver ilə başlatmaq, yalnız options parametri istifadə edilir
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

# Linki açın
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
driver.get(url)

# Sayfanın tam yüklənməsini gözləyirik
time.sleep(5)

# Tokeni tapmağa çalışırıq
try:
    # Tokeni script tagı içərisindən çıxarmaq
    script_content = driver.find_element(By.XPATH, "//script[contains(text(),'tkn=')]").get_attribute("innerHTML")
    token = script_content.split('tkn=')[1].split('&')[0]  # Tokeni alırıq
    with open("token.txt", "w") as token_file:
        token_file.write(token)  # Tokeni fayla yazırıq
    print("✅ Token tapıldı və 'token.txt' faylına yazıldı.")
except Exception as e:
    print(f"❌ Token tapılmadı! Hata: {str(e)}")
finally:
    driver.quit()
