import os
import requests
import zipfile
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  # ✅ ChromeDriver avtomatik yüklənməsi üçün

# 🔄 ChromeDriver yükləyən və qaytaran funksiya
def get_chromedriver():
    try:
        print("ChromeDriver yüklənir...")
        chrome_driver_path = ChromeDriverManager().install()  # ✅ Düzgün versiya avtomatik yüklənir
        print("ChromeDriver uğurla yükləndi.")
        return chrome_driver_path
    except Exception as e:
        print(f"ChromeDriver yükləmə xətası: {e}")
        return None

# 🔎 M3U8 linkini tapmaq üçün funksiya
def get_m3u8_from_network():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        chrome_driver_path = get_chromedriver()
        if not chrome_driver_path:
            return None

        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
        driver.get(url)

        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "video")))

        try:
            m3u8_link = driver.execute_script("return document.querySelector('video').src;")
            print(f"JavaScript ilə tapılan M3U8 linki: {m3u8_link}")
        except Exception:
            m3u8_link = None

        if not m3u8_link:
            logs = driver.get_log("performance")
            for entry in logs:
                try:
                    log = json.loads(entry["message"])
                    if "method" in log and log["method"] == "Network.responseReceived":
                        url = log["params"]["response"]["url"]
                        if "m3u8" in url:
                            m3u8_link = url
                            print(f"M3U8 linki tapıldı: {m3u8_link}")
                            break
                except Exception:
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
        return re.sub(r"tkn=[^&]*", f"tkn={new_token}", url)
    except Exception as e:
        print(f"Token yeniləmək xətası: {e}")
        return None

# 🔄 Yerli fayla M3U8 linkini yazan funksiya
def write_to_local_file(m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, fayl yenilənmədi."
    try:
        new_content = f"#EXTM3U\n#EXTINF:-1,xezer tv\n{m3u8_link}\n"
        file_path = os.path.abspath("token.txt")
        with open(file_path, "w") as file:
            file.write(new_content)
        print("Yerli fayl uğurla yeniləndi.")
    except Exception as e:
        print(f"Fayla yazma xətası: {e}")
        return f"Fayla yazma xətası: {e}"

# 🔄 Əsas işləyən funksiya
def main():
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"
    m3u8_link = get_m3u8_from_network()
    if m3u8_link:
        updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
        print(f"Yeni M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 tapılmadı.")
        return
    write_to_local_file(updated_m3u8_link)

if __name__ == "__main__":
    main()
