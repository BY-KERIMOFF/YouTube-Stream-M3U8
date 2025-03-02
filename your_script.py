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

# 🔄 ChromeDriver əl ilə yükləyən funksiya
def download_chromedriver():
    try:
        chrome_driver_url = "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.0/win64/chromedriver-win64.zip"
        chrome_driver_zip = "chromedriver-win64.zip"

        print("ChromeDriver yüklənir...")
        response = requests.get(chrome_driver_url)
        if response.status_code == 200:
            with open(chrome_driver_zip, "wb") as file:
                file.write(response.content)
            print("ChromeDriver uğurla yükləndi.")

            with zipfile.ZipFile(chrome_driver_zip, 'r') as zip_ref:
                zip_ref.extractall("chrome_driver")
            print("ChromeDriver çıxarıldı.")
            os.remove(chrome_driver_zip)
        else:
            print(f"Yükləmə zamanı xəta baş verdi. Status kodu: {response.status_code}")
    except Exception as e:
        print(f"ChromeDriver yükləmə xətası: {e}")

# 🔎 M3U8 linkini tapmaq üçün funksiya
def get_m3u8_from_network():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        chrome_driver_path = os.path.join(os.getcwd(), "chrome_driver", "chromedriver.exe")
        if not os.path.exists(chrome_driver_path):
            download_chromedriver()

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

# 🔄 Əsas işləyən funksiya
def main():
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"
    m3u8_link = get_m3u8_from_network()
    if m3u8_link:
        updated_m3u8_link = re.sub(r"tkn=[^&]*", f"tkn={new_token}", m3u8_link)
        print(f"Yeni M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 tapılmadı.")
        return
    with open("token.txt", "w") as file:
        file.write(f"#EXTM3U\n#EXTINF:-1,xezer tv\n{updated_m3u8_link}\n")
    print("Yerli fayl uğurla yeniləndi.")

if __name__ == "__main__":
    main()
