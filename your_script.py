import os
import requests
import zipfile
import json
import re
import platform
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_chrome_version():
    try:
        if platform.system() == "Windows":
            import winreg
            reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                version, _ = winreg.QueryValueEx(key, "version")
                return version
        elif platform.system() == "Linux":
            import subprocess
            result = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True)
            version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
            return version_match.group(1) if version_match else None
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], capture_output=True, text=True)
            version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
            return version_match.group(1) if version_match else None
        else:
            return None
    except Exception as e:
        print(f"Chrome versiyası tapılmadı: {e}")
        return None

def download_chromedriver():
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("Chrome versiyası tapılmadı!")
        return

    major_version = chrome_version.split(".")[0]
    os_type = "win64" if platform.system() == "Windows" else "linux64" if platform.system() == "Linux" else "mac64"
    chromedriver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{major_version}.0.0.0/{os_type}/chromedriver-{os_type}.zip"
    zip_path = "chromedriver.zip"
    
    print("ChromeDriver yüklənir...")
    response = requests.get(chromedriver_url)
    if response.status_code == 200:
        with open(zip_path, "wb") as file:
            file.write(response.content)
        print("ChromeDriver uğurla yükləndi.")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("chrome_driver")
        os.remove(zip_path)
        chromedriver_path = os.path.join(os.getcwd(), "chrome_driver", "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
        os.chmod(chromedriver_path, 0o755)
    else:
        print("ChromeDriver yükləmə xətası! Versiya tapılmadı.")

def get_m3u8_from_network():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    chromedriver_path = os.path.join(os.getcwd(), "chrome_driver", "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
    if not os.path.exists(chromedriver_path):
        download_chromedriver()

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "video")))
    
    try:
        m3u8_link = driver.execute_script("return document.querySelector('video').src;")
    except Exception as e:
        print(f"Video src tapılmadı: {e}")
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
                        break
            except Exception as e:
                print(f"Log analizi xətası: {e}")
                continue

    driver.quit()
    return m3u8_link

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
