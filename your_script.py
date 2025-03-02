import os
import re
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_m3u8_from_network():
    """M3U8 linkini tapır."""
    # Chrome seçimlərini təyin et
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless modda işləmək üçün
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Chrome və ChromeDriver yollarını təyin edin
    chrome_path = os.path.join(os.getcwd(), "chrome-linux64", "chrome")
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver-linux64", "chromedriver")

    chrome_options.binary_location = chrome_path

    # ChromeDriver-i başlat
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)

    try:
        # M3U8 linkini tapmaq üçün səhifəyə daxil ol
        url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
        driver.get(url)

        # İframe-i gözlə və ona keç
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)

        # Video elementi gözlə
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "video")))

        # M3U8 linkini tap
        m3u8_link = driver.execute_script("return document.querySelector('video').src;")
        if not m3u8_link:
            print("M3U8 linki tapılmadı! Şəbəkə logları yoxlanılır...")
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

        return m3u8_link
    except Exception as e:
        print(f"M3U8 linki tapılmadı: {e}")
        return None
    finally:
        # Brauzeri bağla
        driver.quit()

def main():
    # Yeni token
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"

    # M3U8 linkini tap
    m3u8_link = get_m3u8_from_network()
    if m3u8_link:
        # Tokeni yenilə
        updated_m3u8_link = re.sub(r"tkn=[^&]*", f"tkn={new_token}", m3u8_link)
        print(f"Yeni M3U8 linki: {updated_m3u8_link}")

        # Fayla yaz
        with open("token.txt", "w") as file:
            file.write(f"#EXTM3U\n#EXTINF:-1,xezer tv\n{updated_m3u8_link}\n")
        print("Yerli fayl uğurla yeniləndi.")
    else:
        print("M3U8 tapılmadı.")

if __name__ == "__main__":
    main()
