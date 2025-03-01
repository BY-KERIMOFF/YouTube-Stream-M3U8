from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import json

def get_m3u8_from_network():
    try:
        options = Options()
        # options.add_argument("--headless")  # Headless rejimini sınaqdan keçirin
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

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

def main():
    m3u8_link = get_m3u8_from_network()
    if not m3u8_link:
        print("M3U8 tapılmadı.")
        return

    print(f"M3U8 linki: {m3u8_link}")

if __name__ == "__main__":
    main()
