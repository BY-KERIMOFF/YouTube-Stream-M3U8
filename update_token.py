import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def get_m3u8_link():
    options = Options()
    options.add_argument("--headless")  # GUI olmadan işləmək
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Səhifəyə daxil olun
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    # Səhifənin tam yüklənməsi üçün gözləyin
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
    time.sleep(5)  # Səhifənin tam yüklənməsi üçün əlavə vaxt
    
    # Iframe-ə keçid edin
    iframe = driver.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframe)  # İframe-ə keçid

    # M3U8 linkini tapın
    try:
        # M3U8 linkini axtarırıq
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//source[contains(@src, 'm3u8')]")))
        m3u8_element = driver.find_element(By.XPATH, "//source[contains(@src, 'm3u8')]")
        m3u8_link = m3u8_element.get_attribute('src')
        print(f"M3U8 linki tapıldı: {m3u8_link}")
    except Exception as e:
        print("M3U8 linki tapılmadı:", e)
        m3u8_link = None
    
    driver.quit()
    return m3u8_link

def update_token_in_url(url, new_token):
    # URL-dəki tokeni dəyişdirmək üçün regex istifadə edirik
    pattern = r"tkn=[^&]*"
    updated_url = re.sub(pattern, f"tkn={new_token}", url)
    print(f"Yeni M3U8 linki: {updated_url}")
    return updated_url

def update_github_repo(token, m3u8_link):
    if m3u8_link is None:
        return "M3U8 linki tapılmadı, repo yenilənmədi."
    
    # GitHub API ilə repo yeniləmək
    owner = "by-kerimoff"  # GitHub istifadəçi adı
    repo = "YouTube-Stream-M3U8"  # Repo adı
    path = "m3u8_link.txt"  # Fayl adı
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    headers = {
        'Authorization': f'token {token}',  # GitHub tokeni
        'Content-Type': 'application/json',
    }
    
    # Faylın mövcud olub-olmamasını yoxlayın
    response = requests.get(github_api_url, headers=headers)
    
    if response.status_code == 200 and "sha" in response.json():
        sha = response.json()["sha"]
    else:
        sha = None
    
    if sha:
        # Fayl mövcuddur, onu yeniləyirik
        content = {
            "message": "Update M3U8 link",
            "content": m3u8_link.encode('utf-8').decode('utf-8'),
            "sha": sha
        }
    else:
        # Fayl mövcud deyilsə, yeni fayl yaradın
        content = {
            "message": "Add M3U8 link",
            "content": m3u8_link.encode('utf-8').decode('utf-8'),
        }
    
    response = requests.put(github_api_url, json=content, headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        return "GitHub repo uğurla yeniləndi, yeni M3U8 linki əlavə edildi."
    else:
        return f"GitHub repo yenilənərkən xəta baş verdi: {response.text}"

def main():
    # Yeni tokeni burada təyin edin
    new_token = "8TrpuFQA8gwPZemNYt3qXA"  # Yeni tokeni buraya əlavə edin
    
    # Əvvəlki linki əldə et
    m3u8_link = get_m3u8_link()
    
    if m3u8_link:
        # Tokeni yeni bir dəyərlə dəyişirik
        updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
        print(f"Güncellenmiş M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 linki tapılmadı.")
        updated_m3u8_link = None
        
    # İkinci linki də əlavə edirik
    additional_link = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=z_x6qXYvRJj7HwDHPWC1tA&tms=1740722575"
    additional_updated_link = update_token_in_url(additional_link, new_token)
    print(f"İkinci M3U8 linki: {additional_updated_link}")
    
    # GitHub repo yeniləməsi
    github_token = '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'  # Burada düzgün tokeni daxil edin
    if updated_m3u8_link:
        result = update_github_repo(github_token, updated_m3u8_link)
        print(result)
    else:
        result = update_github_repo(github_token, additional_updated_link)
        print(result)

if __name__ == "__main__":
    main()
