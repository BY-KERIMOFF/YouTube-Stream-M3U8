import time
import json
import re
import os
import requests
import base64
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
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

        # Iframe-ə keçid edirik
        try:
            iframe = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)
            print("Iframe-ə keçid edildi.")
        except Exception as e:
            print(f"Iframe tapılmadı: {e}")

        # Video elementinin yüklənməsini gözləyirik
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            print("Video elementi tapıldı.")
        except Exception as e:
            print(f"Video elementi tapılmadı: {e}")

        # JavaScript ilə M3U8 linkini tapmağa çalışırıq
        try:
            m3u8_link = driver.execute_script("return document.querySelector('video').src;")
            print(f"JavaScript ilə tapılan M3U8 linki: {m3u8_link}")
        except Exception as e:
            print(f"JavaScript ilə M3U8 linki tapılmadı: {e}")
            m3u8_link = None

        # Əgər JavaScript ilə tapılmadısa, logları təhlil edirik
        if not m3u8_link:
            logs = driver.get_log("performance")
            print("Network logları:")
            for entry in logs:
                try:
                    log = json.loads(entry["message"])  # Log məlumatını JSON formatında oxu
                    if "method" in log and log["method"] == "Network.responseReceived":
                        url = log["params"]["response"]["url"]
                        print(f"Tapılan URL: {url}")
                        if "m3u8" in url:  # M3U8 linkini axtar
                            m3u8_link = url
                            print(f"M3U8 linki tapıldı: {m3u8_link}")
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

# 🔄 Yerli fayla M3U8 linkini yazan funksiya
def write_to_local_file(m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, fayl yenilənmədi."

    try:
        # Yeni məzmunu hazırlayırıq
        new_content = f"#EXTM3U\n#EXTINF:-1,xezer tv\n{m3u8_link}\n"

        # Faylın tam yolunu müəyyən edirik
        file_path = os.path.abspath("token.txt")
        print(f"Fayl yaradılacaq yol: {file_path}")

        # Yerli fayla yazırıq
        with open(file_path, "w") as file:
            file.write(new_content)
        print("Yerli fayl uğurla yeniləndi.")
    except Exception as e:
        print(f"Fayla yazma xətası: {e}")
        return f"Fayla yazma xətası: {e}"

# 🔄 GitHub-da M3U8 linkini yeniləyən funksiya
def update_github_repo(github_token, m3u8_link):
    owner = "by-kerimoff"
    repo = "YouTube-Stream-M3U8"
    path = "token.txt"
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # Faylı oxuyuruq
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

        # Yeni məzmunu hazırlayırıq
        new_content = f"#EXTM3U\n#EXTINF:-1,xezer tv\n{m3u8_link}\n"
        content_base64 = base64.b64encode(new_content.encode()).decode()  # Base64 formatına salırıq

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

    except Exception as e:
        print(f"GitHub yeniləmə xətası: {e}")
        return f"GitHub-da xəta baş verdi: {e}"

# 🔄 Əsas işləyən funksiya
def main():
    # Yeni tokeni daxil et
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"  # Yenilənməli olan token
    github_token = "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"  # GitHub tokeni

    # Saytdan yeni M3U8 linkini götür
    m3u8_link = get_m3u8_from_network()

    if m3u8_link:
        updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
        print(f"Yeni M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 tapılmadı.")
        return

    # Yerli fayla yaz
    result = write_to_local_file(updated_m3u8_link)
    print(result)

    # GitHub repo-nu yenilə
    result = update_github_repo(github_token, updated_m3u8_link)
    print(result)

# 🏃‍♂️ Skripti işə sal
if __name__ == "__main__":
    main()
