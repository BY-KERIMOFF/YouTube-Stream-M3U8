import tempfile
import os
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Loglama konfiqurasiyası
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("script.log"), logging.StreamHandler()],
)

CONFIG = {
    "url": "https://www.ecanlitvizle.app/xezer-tv-canli-izle/",
    "iframe_wait_time": 30,
    "video_wait_time": 15,
    "headless": True,
}

def setup_driver():
    try:
        options = Options()
        if CONFIG["headless"]:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logging.error(f"ChromeDriver quraşdırılarkən xəta: {e}")
        return None

def get_m3u8_from_network(driver):
    try:
        driver.get(CONFIG["url"])
        logging.info(f"Səhifə yükləndi: {CONFIG['url']}")

        WebDriverWait(driver, CONFIG["iframe_wait_time"]).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            logging.info("Iframe-ə keçid edildi.")

        WebDriverWait(driver, CONFIG["video_wait_time"]).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        logging.info("Video elementi tapıldı.")

        logs = driver.get_log("performance")
        m3u8_links = set()
        
        for entry in logs:
            log = json.loads(entry["message"])
            if "method" in log and log["method"] == "Network.responseReceived":
                url = log.get("params", {}).get("response", {}).get("url", "")
                if "m3u8" in url:
                    m3u8_links.add(url)
                    logging.info(f"Tapıldı: {url}")
        
        if m3u8_links:
            return list(m3u8_links)
        
        logging.warning("M3U8 linki tapılmadı.")
        return None
    except Exception as e:
        logging.error(f"M3U8 linki əldə edilərkən xəta: {e}")
        return None

def write_to_file(m3u8_links):
    if m3u8_links:
        with open("token.txt", "w") as file:
            for link in m3u8_links:
                file.write(link + "\n")
        logging.info("Fayl uğurla yaradıldı.")
    else:
        logging.warning("M3U8 linki tapılmadı, fayl yaradılmadı.")

def main():
    driver = setup_driver()
    if not driver:
        return

    m3u8_links = get_m3u8_from_network(driver)
    write_to_file(m3u8_links)

    driver.quit()
    logging.info("ChromeDriver bağlandı.")

    if os.path.exists("token.txt") and os.path.getsize("token.txt") > 0:
        logging.info("token.txt faylı mövcuddur və boş deyil.")
        os.system("git add token.txt")
        os.system("git commit -m 'Auto-update token.txt'")
        os.system("git push")
    else:
        logging.error("token.txt faylı mövcud deyil və ya boşdur!")
        exit(1)

if __name__ == "__main__":
    main()
