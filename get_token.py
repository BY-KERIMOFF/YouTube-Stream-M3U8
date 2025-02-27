import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Chrome'u başlatmaq üçün konfigurasiya
chrome_options = Options()
chrome_options.add_argument("--headless")  # Chrome'u başsız rejimdə işə salırıq
chrome_options.add_argument("--no-sandbox")

# Selenium ilə WebDriver'i işə salırıq
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# İstifadə edəcəyiniz veb səhifənin URL-i
url = 'https://str.yodacdn.net/ictimai/tracks-v1a1/mono.ts.m3u8?token=c5f9a100d0f50adb10857d880bd5c9d2bdd8ac92-cf9b3020cb44ff6cbbfc574f0e977f29-1740699906-1740689106'

# Səhifəyə keçirik
driver.get(url)

# Tokeni tapmaq üçün Selenium ilə elementi tapırıq
# Bu XPath-i düzgün şəkildə təyin etdiyinizdən əmin olun, burada misal olaraq təyin edilmişdir
try:
    token_element = driver.find_element(By.XPATH, "//element_xpath_token")  # Burada doğru XPath'ı yazın
    new_token = token_element.get_attribute('value')  # Tokeni alırıq
    print(f"Yeni token: {new_token}")

    # M3U faylını yeniləyirik
    def update_m3u(token):
        m3u_content = "#EXTM3U\n#EXTINF:-1,İctimai TV\n" + token
        with open("token.m3u8", "w") as file:
            file.write(m3u_content)
        print("M3U faylı yeniləndi!")

    # Tokeni əlavə edirik
    update_m3u(new_token)

except Exception as e:
    print("Token tapılmadı:", str(e))

finally:
    # WebDriver'i bağlayırıq
    driver.quit()
