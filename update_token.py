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
    "headless": True,  # GitHub Actions-da headless rejimi aktiv olmalıdır
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

        # M3U8 linklərini şəbəkə loglarından çıxar
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
    """M3U8 linklərini fayla yaz."""
    if m3u8_links:
        with open("token.txt", "w") as file:
            for link in m3u8_links:
                file.write(link + "\n")
        logging.info("Fayl uğurla yaradıldı.")
    else:
        logging.warning("M3U8 linki tapılmadı, fayl yaradılmadı.")

def main():
    """Əsas funksiya."""
    driver = setup_driver()
    if not driver:
        return

    m3u8_links = get_m3u8_from_network(driver)
    write_to_file(m3u8_links)

    driver.quit()
    logging.info("ChromeDriver bağlandı.")

if __name__ == "__main__":
    main()
