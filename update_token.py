import time
import requests
import base64
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔎 M3U8 linkini tapmaq üçün network traffic-i yoxlayan funksiya
def get_m3u8_from_network():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)

    # Sayfanın yüklənməsini gözləyirik
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

    logs = driver.get_log("performance")
    m3u8_link = None
    for entry in logs:
        try:
            log = json.loads(entry["message"])["message"]
            if log["method"] == "Network.responseReceived":
                url = log["params"]["response"]["url"]
                if "xazartv.m3u8" in url:
                    m3u8_link = url
                    break
        except Exception as e:
            print(f"Xəta baş verdi: {e}")
            continue

    driver.quit()
    return m3u8_link

# 🔄 Tokeni yeniləyən funksiya
def update_token_in_url(url, new_token):
    if not url:
        return None
    updated_url = re.sub(r"tkn=[^&]*", f"tkn={new_token}", url)
    return updated_url

# 🔄 GitHub-da M3U8 linkini yeniləyən funksiya
def update_github_repo(github_token, m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, repo yenilənmədi."

    owner = "by-kerimoff"
    repo = "YouTube-Stream-M3U8"
    path = "xezer_tv.m3u8"
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(github_api_url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    if response.status_code == 404:
        return "Fayl tapılmadı, yeni fayl yaradılır."
    elif response.status_code == 500:
        return "GitHub serverində xəta baş verdi."

    content = base64.b64encode(m3u8_link.encode()).decode()  # Base64 formatına salırıq
    data = {
        "message": "Update Xezer TV M3U8 link",
        "content": content,
        "sha": sha
    } if sha else {
        "message": "Add Xezer TV M3U8 link",
        "content": content
    }

    response = requests.put(github_api_url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        return "GitHub repo uğurla yeniləndi."
    else:
        return f"Xəta: {response.text}"

# 🔄 Əsas işləyən funksiya
def main():
    # Yeni tokeni daxil et
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"  # Yenilənməli olan token
    github_token = "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"  # Burada öz GitHub tokenini yaz

    # Saytdan yeni M3U8 linkini götür
    m3u8_link = get_m3u8_from_network()

    if m3u8_link:
        updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
        print(f"Yeni M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 tapılmadı.")
        return

    # GitHub repo-nu yenilə
    result = update_github_repo(github_token, updated_m3u8_link)
    print(result)

# 🏃‍♂️ Skripti işə sal
if __name__ == "__main__":
    main()
