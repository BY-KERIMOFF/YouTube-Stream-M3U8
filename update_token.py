import time
import json
import re
import os
import requests
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, urlencode
from webdriver_manager.chrome import ChromeDriverManager

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

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "video")))

        try:
            m3u8_link = driver.execute_script("return document.querySelector('video').src;")
        except:
            m3u8_link = None

        if not m3u8_link:
            logs = driver.get_log("performance")
            for entry in logs:
                log = json.loads(entry["message"])
                if "method" in log and log["method"] == "Network.responseReceived":
                    url = log["params"]["response"]["url"]
                    if "m3u8" in url:
                        m3u8_link = url
                        break

        driver.quit()
        return m3u8_link
    except Exception as e:
        print(f"Xəta: {e}")
        return None

def update_token_in_url(url, new_token):
    if not url:
        return None

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params["tkn"] = [new_token]  # Yeni tokeni əlavə et

    updated_query = urlencode(query_params, doseq=True)
    updated_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{updated_query}"
    return updated_url

def write_to_local_file(m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, fayl yenilənmədi."

    try:
        new_content = f"#EXTM3U\n#EXTINF:-1,xezer tv\n{m3u8_link}\n"
        file_path = os.path.abspath("token.txt")

        with open(file_path, "w") as file:
            file.write(new_content)

        return "Yerli fayl uğurla yeniləndi."
    except Exception as e:
        return f"Fayla yazma xətası: {e}"

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
        response = requests.get(github_api_url, headers=headers)
        sha = response.json().get("sha") if response.status_code == 200 else None

        new_content = f"#EXTM3U\n#EXTINF:-1,xezer tv\n{m3u8_link}\n"
        content_base64 = base64.b64encode(new_content.encode()).decode()

        data = {
            "message": "Update Xezer TV M3U8 link",
            "content": content_base64,
            "sha": sha
        } if sha else {
            "message": "Add Xezer TV M3U8 link",
            "content": content_base64
        }

        response = requests.put(github_api_url, json=data, headers=headers)
        return "GitHub repo uğurla yeniləndi." if response.status_code in [200, 201] else f"GitHub səhvi: {response.text}"

    except Exception as e:
        return f"GitHub-da xəta baş verdi: {e}"

def main():
    new_token = os.getenv("NEW_TOKEN", "default_token")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("GitHub token tapılmadı. Mühit dəyişənini yoxlayın.")
        return

    m3u8_link = get_m3u8_from_network()
    if not m3u8_link:
        print("M3U8 tapılmadı.")
        return

    updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
    print(write_to_local_file(updated_m3u8_link))
    print(update_github_repo(github_token, updated_m3u8_link))

if __name__ == "__main__":
    main()
