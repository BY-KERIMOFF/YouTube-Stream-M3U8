from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def update_token():
    # Chrome'u başlatmaq üçün konfiqurasiya
    options = Options()
    options.add_argument("--headless")  # Headless rejimində çalışır (ekran olmadan)
    driver = webdriver.Chrome(options=options)
    
    # URL-ni yükləyirik
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    # Səhifənin tam yüklənməsi üçün gözləyirik
    time.sleep(5)  # 5 saniyə gözləyirik (bunu səhifənin yüklənmə sürətinə görə tənzimləyə bilərsiniz)
    
    try:
        # Token-i tapmağa çalışırıq (burada doğru CSS seçicisini istifadə etməliyik)
        # Misal üçün: 
        token_element = driver.find_element(By.CSS_SELECTOR, "input[name='token']")
        token = token_element.get_attribute('value')
        
        # Əgər token tapılarsa, onu ekrana çıxarırıq
        if token:
            print(f"Yeni Token: {token}")
            new_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740712041"
            print(f"Yeni URL: {new_url}")
        else:
            print("Token tapılmadı!")

    except Exception as e:
        print(f"Səhv: {e}")

    # Brauzeri bağlayırıq
    driver.quit()

# Skripti işə salırıq
if __name__ == "__main__":
    update_token()
