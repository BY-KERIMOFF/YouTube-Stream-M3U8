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
import base64

def get_m3u8_link():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
    time.sleep(10)
    
    try:
        m3u8_element = driver.find_element(By.XPATH, "//a[contains(@href, 'm3u8')]")
        m3u8_link = m3u8_element.get_attribute('href')
        print(f"M3U8 linki tapıldı: {m3u8_link}")
    except Exception as e:
        print("M3U8 linki tapılmadı.")
        m3u8_link = None
    
    driver.quit()
    return m3u8_link

def update_token_in_url(url, new_token):
    pattern = r"tkn=[^&]*"
    updated_url = re.sub(pattern, f"tkn={new_token}", url)
    if updated_url == url:
        print("Token tapılmadı və ya dəyişdirilmədi.")
    else:
        print(f"Yeni M3U8 linki: {updated_url}")
    return updated_url

def update_github_repo(token, m3u8_link):
    if m3u8_link is None:
        return "M3U8 linki tapılmadı, repo yenilənmədi."
    
    owner = "by-kerimoff"
    repo = "YouTube-Stream-M3U8"
    path = "m3u8_link.txt"
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    
    headers = {
        'Authorization': f'token {token}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(github_api_url, headers=headers)
    
    if response.status_code == 404:
        content = {
            "message": "Add M3U8 link",
            "content": base64.b64encode(m3u8_link.encode('utf-8')).decode('utf-8'),
        }
        response = requests.put(github_api_url, json=content, headers=headers)
        if response.status_code == 201:
            return "GitHub repo yeniləndi, yeni M3U8 linki əlavə edildi."
        else:
            return f"GitHub repo yenilənərkən xəta baş verdi: {response.text}"
    else:
        content = {
            "message": "Update M3U8 link",
            "content": base64.b64encode(m3u8_link.encode('utf-8')).decode('utf-8'),
            "sha": response.json()["sha"]
        }
        response = requests.put(github_api_url, json=content, headers=headers)
        if response.status_code == 200:
            return "GitHub repo uğurla yeniləndi, yeni M3U8 linki əlavə edildi."
        else:
            return f"GitHub repo yenilənərkən xəta baş verdi: {response.text}"

def main():
    new_token = "8TrpuFQA8gwPZemNYt3qXA"
    m3u8_link = get_m3u8_link()
    
    if m3u8_link:
        updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
        print(f"Güncellenmiş M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 linki tapılmadı.")
        updated_m3u8_link = None
        
    additional_link = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=8TrpuFQA8gwPZemNYt3qXA&tms=1740719676"
    additional_updated_link = update_token_in_url(additional_link, new_token)
    print(f"İkinci M3U8 linki: {additional_updated_link}")
    
    github_token = 'YOUR_GITHUB_TOKEN'
    if updated_m3u8_link:
        result = update_github_repo(github_token, updated_m3u8_link)
        print(result)
    else:
        result = update_github_repo(github_token, additional_updated_link)
        print(result)

if __name__ == "__main__":
    main()
