import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import json
import logging

# Loglama konfiqurasiyası
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("script.log"), logging.StreamHandler()],
)

# Konfiqurasiya dəyişənləri
CONFIG = {
    "url": "https://www.ecanlitvizle.app/xezer-tv-canli-izle/",
    "iframe_wait_time": 30,
    "video_wait_time": 15,
    "headless": False,  # Headless rejimi
}

def setup_driver():
    """ChromeDriver-i quraşdır və başlat."""
    try:
        options = Options()
        if CONFIG["headless"]:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        # Unikal bir qovluq yaradın
        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logging.error(f"ChromeDriver quraşdırılarkən xəta: {e}")
        return None

def get_m3u8_from_network(driver):
    """M3U8 linkini əldə et."""
    try:
        driver.get(CONFIG["url"])
        logging.info(f"Səhifə yükləndi: {CONFIG['url']}")

        # iframe-i gözlə
        WebDriverWait(driver, CONFIG["iframe_wait_time"]).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            logging.info("Iframe-ə keçid edildi.")

        # Video elementini gözlə
        WebDriverWait(driver, CONFIG["video_wait_time"]).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        logging.info("Video elementi tapıldı.")

        # M3U8 linkini əldə et
        m3u8_link = driver.execute_script("return document.querySelector('video').src;")
        if m3u8_link:
            logging.info(f"M3U8 linki tapıldı: {m3u8_link}")
            return m3u8_link

        # Şəbəkə loglarından M3U8 linkini axtar
        logs = driver.get_log("performance")
        for entry in logs:
            log = json.loads(entry["message"])
            if "method" in log and log["method"] == "Network.responseReceived":
                url = log["params"]["response"]["url"]
                if "m3u8" in url:
                    logging.info(f"Şəbəkə loglarından M3U8 linki tapıldı: {url}")
                    return url

        logging.warning("M3U8 linki tapılmadı.")
        return None

    except Exception as e:
        logging.error(f"M3U8 linki əldə edilərkən xəta: {e}")
        return None

def main():
    """Əsas funksiya."""
    driver = setup_driver()
    if not driver:
        return

    m3u8_link = get_m3u8_from_network(driver)
    if m3u8_link:
        print(f"M3U8 linki: {m3u8_link}")
    else:
        print("M3U8 tapılmadı.")

    driver.quit()
    logging.info("ChromeDriver bağlandı.")

if __name__ == "__main__":
    main()
