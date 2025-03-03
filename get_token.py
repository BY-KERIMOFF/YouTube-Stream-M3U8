import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Chrome başlatma opsiyaları
options = Options()
options.add_argument("--headless")  # Chrome'u görünməz olaraq işlətmək

# Webdriver'ı qururuq
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Verilən URL (sizin istədiyiniz link)
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# URL-ə gedirik
driver.get(url)

# Tokeni tapmaq üçün səhifənin tam yüklənməsini gözləyirik
driver.implicitly_wait(10)

# Səhifədəki scripti tapırıq və tokeni çıxarırıq
try:
    # Scripti tapırıq və tokeni çıxarırıq
    page_source = driver.page_source
    match = re.search(r'tkn=([A-Za-z0-9_-]+)', page_source)
    
    if match:
        old_token = match.group(1)
        print(f"Eski Token tapıldı: {old_token}")
        
        # Yeni tokeni buraya daxil edin (bu misaldır, əslində yenisini bir şəkildə əldə etməlisiniz)
        new_token = "YeniToken_1234567890"
        
        # URL-dəki tokeni yeniləyirik
        new_url = re.sub(r'tkn=[A-Za-z0-9_-]+', f'tkn={new_token}', url)
        print(f"Yeni URL: {new_url}")
        
        # Yeni URL-ni stream_link.txt faylına yazırıq
        with open("stream_link.txt", "w") as file:
            file.write(new_url)
            print("Yeni URL stream_link.txt faylına yazıldı.")
    else:
        print("Token tapılmadı!")
except Exception as e:
    print(f"Xəta baş verdi: {e}")
finally:
    driver.quit()
