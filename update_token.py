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
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
        driver.get(url)

        # Sayfanın yüklənməsini gözləyirik (daha uzun gözləmə müddəti)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

        logs = driver.get_log("performance")
        m3u8_link = None
        print("Network logları:")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if log["method"] == "Network.responseReceived":
                    url = log["params"]["response"]["url"]
                    print(f"Tapılan URL: {url}")  # Logları çap edirik
                    if "xazartv.m3u8" in url:
                        m3u8_link = url
                        break
            except Exception as e:
                print(f"Xəta baş verdi: {e}")
                continue

        driver.quit()
        return m3u8_link
    except Exception as e:
        print(f"Network yaxalama xətası: {e}")
        return None

# 🔄 Tokeni yeniləyən funksiya
def update_token_in_url(url, new_token):
    try:
        if not url:
            return None
        updated_url = re.sub(r"tkn=[^&]*", f"tkn={new_token}", url)
        return updated_url
    except Exception as e:
        print(f"Token yeniləmək xətası: {e}")
        return None

# 🔄 GitHub-da M3U8 linkini yeniləyən funksiya
def update_github_repo(github_token, m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, repo yenilənmədi."

    owner = "by-kerimoff"
    repo = "YouTube-Stream-M3U8"
    path = "xezer_tv.m3u8"
    txt_path = "xezer_tv_link.txt"  # Yeni .txt faylının adı
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    txt_github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{txt_path}"

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # M3U8 faylını yeniləyirik
        response = requests.get(github_api_url, headers=headers)
        if response.status_code == 200:
            sha = response.json().get("sha")
            print(f"Fayl mövcuddur, SHA: {sha}")
        elif response.status_code == 404:
            sha = None
            print("Fayl tapılmadı, yeni fayl yaradılacaq.")
        else:
            print(f"GitHub API səhvi: {response.text}")
            return f"GitHub API səhvi: {response.text}"

        # Faylın yenilənməsi və ya yeni fayl yaradılması
        content_base64 = base64.b64encode(m3u8_link.encode()).decode()  # Base64 formatına salırıq
        print(f"Base64 kodlaşdırılmış məzmun: {content_base64[:100]}...")  # Məzmunu yoxlayaq

        data = {
            "message": "Update Xezer TV M3U8 link",
            "content": content_base64,
            "sha": sha
        } if sha else {
            "message": "Add Xezer TV M3U8 link",
            "content": content_base64
        }

        # PUT sorğusu ilə fayl yenilənir
        response = requests.put(github_api_url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            print("GitHub repo M3U8 linki ilə uğurla yeniləndi.")
        else:
            print(f"GitHub API sorğusunda xəta: {response.text}")
            return f"GitHub API sorğusunda xəta: {response.text}"

        # .txt faylında M3U8 linkini qeyd edirik (müxtəlif olaraq, burada sadə mətn yazırıq)
        txt_data = {
            "message": "Add Xezer TV M3U8 link to TXT",
            "content": m3u8_link  # M3U8 linkini sadə mətn kimi göndəririk
        }

        # PUT sorğusu ilə yeni .txt fayl yaradılır və link qeyd olunur
        response_txt = requests.put(txt_github_api_url, json=txt_data, headers=headers)
        if response_txt.status_code in [200, 201]:
            print("GitHub repo-da .txt fayl ilə link uğurla qeyd edildi.")
        else:
            print(f"GitHub API sorğusunda .txt faylı xətası: {response_txt.text}")
            return f"GitHub API sorğusunda .txt faylı xətası: {response_txt.text}"

    except Exception as e:
        print(f"GitHub yeniləmə xətası: {e}")
        return f"GitHub-da xəta baş verdi: {e}"

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
