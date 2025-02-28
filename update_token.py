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
    options = Options()
    options.add_argument("--headless")  # GUI olmadan işləmək
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Səhifəyə daxil olun
    url = "https://www.ecanlitvizle.app/trt-1-canli-izle-hd-9/"
    driver.get(url)
    
    # Səhifənin tam yüklənməsi üçün gözləyin
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
    time.sleep(5)  # Səhifənin tam yüklənməsi üçün əlavə vaxt
    
    # M3U8 linkini tapın
    try:
        # M3U8 linkini axtarırıq
        m3u8_element = driver.find_element(By.XPATH, "//a[contains(@href, 'm3u8')]")
        m3u8_link = m3u8_element.get_attribute('href')
        print(f"M3U8 linki tapıldı: {m3u8_link}")
    except Exception as e:
        print("M3U8 linki tapılmadı.")
        m3u8_link = None
    
    driver.quit()
    return m3u8_link

def update_github_repo(token, m3u8_link):
    if m3u8_link is None:
        return "M3U8 linki tapılmadı, repo yenilənmədi."
    
    # GitHub API ilə repo yeniləmək
    github_api_url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
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
        return "Fayl mövcuddur, amma əlavə etmə əməliyyatı uğursuz oldu."

def main():
    m3u8_link = get_m3u8_link()
    github_token = 'YOUR_GITHUB_TOKEN'  # GitHub tokeninizi buraya əlavə edin
    result = update_github_repo(github_token, m3u8_link)
    print(result)

if __name__ == "__main__":
    main()
