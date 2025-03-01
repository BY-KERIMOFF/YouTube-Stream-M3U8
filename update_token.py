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
    github_token = "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"  # Burada öz GitHub tokenini yaz

    # Verilən tokenli linklər
    tokenli_linkler = {
        "xezer_tv": "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=829DLSOSxS-rytI608bLOQ&tms=1740815292",
        "aztv": "https://ecanlitv3.etvserver.com/aztv.m3u8?tkn=78G5M8aZ5F0zCSpGckbKKA&tms=1740815329"
    }

    # Hər bir kanal üçün tokeni yenilə və GitHub repo-suna əlavə et
    for channel_name, url in tokenli_linkler.items():
        updated_url = update_token_in_url(url, new_token)
        if updated_url:
            print(f"Yeni {channel_name} M3U8 linki: {updated_url}")
            update_github_repo(github_token, updated_url, channel_name)
        else:
            print(f"{channel_name} üçün M3U8 linki yenilənmədi.")

# 🏃‍♂️ Skripti işə sal
if __name__ == "__main__":
    main()
