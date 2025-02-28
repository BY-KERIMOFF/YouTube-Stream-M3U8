import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_m3u8_link():
    # Chrome seçimləri
    options = Options()
    options.add_argument("--headless")  # GUI olmadan işləmək
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # ChromeDriver-i yüklə və başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Sayta daxil ol
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    # Səhifənin tam yüklənməsini gözlə
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        print("Səhifə uğurla yükləndi.")
    except Exception as e:
        print("Səhifə yüklənmədi:", e)
        driver.quit()
        return None
    
    # iframe-i tap və ona keçid et
    try:
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)
        print("Iframe-ə keçid edildi.")
    except Exception as e:
        print("Iframe tapılmadı:", e)
        driver.quit()
        return None
    
    # M3U8 linkini tap
    try:
        m3u8_element = driver.find_element(By.XPATH, "//a[contains(@href, 'm3u8')]")
        m3u8_link = m3u8_element.get_attribute('href')
        print(f"M3U8 linki tapıldı: {m3u8_link}")
    except Exception as e:
        print("M3U8 linki tapılmadı:", e)
        m3u8_link = None
    
    # Brauzeri bağla
    driver.quit()
    return m3u8_link

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
    
    if response.status_code == 404:
        # Fayl mövcud deyilsə, yeni fayl yaradın
        content = {
            "message": "Add M3U8 link",
            "content": m3u8_link.encode('utf-8').decode('utf-8'),  # Base64 ilə kodlanmış mətn
        }
        response = requests.put(github_api_url, json=content, headers=headers)
        if response.status_code == 201:
            return "GitHub repo yeniləndi, yeni M3U8 linki əlavə edildi."
        else:
            return f"GitHub repo yenilənərkən xəta baş verdi: {response.text}"
    else:
        # Fayl mövcuddur, onu yeniləyirik
        content = {
            "message": "Update M3U8 link",
            "content": m3u8_link.encode('utf-8').decode('utf-8'),
            "sha": response.json()["sha"]  # Faylın mövcud SHA kodunu istifadə edirik
        }
        response = requests.put(github_api_url, json=content, headers=headers)
        if response.status_code == 200:
            return "GitHub repo uğurla yeniləndi, yeni M3U8 linki əlavə edildi."
        else:
            return f"GitHub repo yenilənərkən xəta baş verdi: {response.text}"

def main():
    # M3U8 linkini əldə et
    m3u8_link = get_m3u8_link()
    
    if m3u8_link:
        print(f"Tapılan M3U8 linki: {m3u8_link}")
    else:
        print("M3U8 linki tapılmadı.")
        return
    
    # GitHub repo yeniləməsi
    github_token = 'YOUR_GITHUB_TOKEN'  # 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
    result = update_github_repo(github_token, m3u8_link)
    print(result)

if __name__ == "__main__":
    main()
