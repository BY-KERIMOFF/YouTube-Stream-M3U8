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
def get_m3u8_from_network(url, channel_name):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        # Sayfanın yüklənməsini gözləyirik (daha uzun gözləmə müddəti)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

        # Iframe-ə keçid et
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)

        # JavaScript ilə yüklənməni gözlə
        time.sleep(10)

        logs = driver.get_log("performance")
        m3u8_link = None
        print(f"{channel_name} üçün network logları:")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if log["method"] == "Network.requestWillBeSent":
                    url = log["params"].get("request", {}).get("url", "")
                elif log["method"] == "Network.responseReceived":
                    url = log["params"].get("response", {}).get("url", "")
                else:
                    continue

                if url and ".m3u8" in url:
                    print(f"Tapılan URL: {url}")
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

# 🔄 GitHub-da kanallar.txt faylını yeniləyən funksiya
def update_github_repo(github_token, m3u8_link, channel_name):
    if not m3u8_link:
        return f"{channel_name} üçün M3U8 linki tapılmadı, repo yenilənmədi."

    owner = "by-kerimoff"
    repo = "YouTube-Stream-M3U8"
    path = "kanallar.txt"  # Fayl adı
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # kanallar.txt faylını yoxlayırıq
        response = requests.get(github_api_url, headers=headers)
        if response.status_code == 200:
            sha = response.json().get("sha")
            existing_content = base64.b64decode(response.json()["content"]).decode()
            print(f"Fayl mövcuddur, SHA: {sha}")
        elif response.status_code == 404:
            sha = None
            existing_content = ""
            print("Fayl tapılmadı, yeni fayl yaradılacaq.")
        else:
            print(f"GitHub API səhvi: {response.text}")
            return f"GitHub API səhvi: {response.text}"

        # Yeni məzmunu əlavə edirik
        new_content = f"{existing_content}\n{channel_name}: {m3u8_link}"
        encoded_content = base64.b64encode(new_content.encode()).decode()

        # Faylın yenilənməsi və ya yeni fayl yaradılması
        data = {
            "message": f"Update {channel_name} M3U8 link",
            "content": encoded_content,
            "sha": sha
        } if sha else {
            "message": f"Add {channel_name} M3U8 link",
            "content": encoded_content
        }

        # PUT sorğusu ilə fayl yenilənir
        response = requests.put(github_api_url, json=data, headers=headers)
        print(f"GitHub API cavabı: {response.status_code}, {response.text}")  # Debug üçün
        if response.status_code in [200, 201]:
            print(f"GitHub repo {channel_name} M3U8 linki ilə uğurla yeniləndi.")
        else:
            print(f"GitHub API sorğusunda xəta: {response.text}")
            return f"GitHub API sorğusunda xəta: {response.text}"

    except Exception as e:
        print(f"GitHub yeniləmə xətası: {e}")
        return f"GitHub-da xəta baş verdi: {e}"

# 🔄 Əsas işləyən funksiya
def main():
    # Yeni tokeni daxil et
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"  # Yenilənməli olan token
    github_token = "yeni_token_buraya_yazın"  # Burada öz GitHub tokenini yaz

    # Xezer TV üçün M3U8 linkini tap
    xezer_tv_url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    xezer_tv_m3u8 = get_m3u8_from_network(xezer_tv_url, "xezer_tv")
    if xezer_tv_m3u8:
        updated_xezer_tv_m3u8 = update_token_in_url(xezer_tv_m3u8, new_token)
        print(f"Yeni Xezer TV M3U8 linki: {updated_xezer_tv_m3u8}")
        update_github_repo(github_token, updated_xezer_tv_m3u8, "xezer_tv")
    else:
        print("Xezer TV üçün M3U8 tapılmadı.")

    # Now TV üçün M3U8 linkini tap
    now_tv_url = "https://www.ecanlitvizle.app/now-tv-canli-izle-3/"
    now_tv_m3u8 = get_m3u8_from_network(now_tv_url, "now_tv")
    if now_tv_m3u8:
        updated_now_tv_m3u8 = update_token_in_url(now_tv_m3u8, new_token)
        print(f"Yeni Now TV M3U8 linki: {updated_now_tv_m3u8}")
        update_github_repo(github_token, updated_now_tv_m3u8, "now_tv")
    else:
        print("Now TV üçün M3U8 tapılmadı.")

# 🏃‍♂️ Skripti işə sal
if __name__ == "__main__":
    main()
