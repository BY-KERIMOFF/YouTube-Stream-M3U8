import time
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Konfiqurasiya parametrləri
CONFIG = {
    "url": "https://www.ecanlitvizle.app/xezer-tv-canli-izle/",  # M3U8 linkini tapmaq istədiyiniz saytın URL-si
    "iframe_wait_time": 10,  # Iframe üçün gözləmə vaxtı
    "video_wait_time": 15,  # Video elementinə baxmaq üçün gözləmə vaxtı
    "log_file": "m3u8_link.txt",  # M3U8 linkinin yazılacağı fayl adı
}

# Logging konfiqurasiyası
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_m3u8_from_network(driver):
    try:
        driver.get(CONFIG["url"])
        logging.info(f"Səhifə yükləndi: {CONFIG['url']}")

        # Iframe-i gözlə
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

        # Video elementinin src atributunu əldə et
        video_element = driver.find_element(By.TAG_NAME, "video")
        m3u8_link = video_element.get_attribute("src")

        if m3u8_link and m3u8_link.startswith("blob:"):
            logging.info("Blob linki tapıldı. Şəbəkə logları təhlil edilir...")
            logs = driver.get_log("performance")
            for entry in logs:
                log = json.loads(entry["message"])
                if "method" in log and log["method"] == "Network.responseReceived":
                    url = log["params"]["response"]["url"]
                    if "m3u8" in url:
                        m3u8_link = url
                        logging.info(f"Şəbəkə loglarından M3U8 linki tapıldı: {m3u8_link}")
                        break

        if m3u8_link:
            logging.info(f"M3U8 linki uğurla tapıldı: {m3u8_link}")
            return m3u8_link

        logging.warning("M3U8 linki tapılmadı.")
        return None

    except Exception as e:
        logging.error(f"M3U8 linki əldə edilərkən xəta: {e}")
        return None

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Başsız rejim
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")  # Chrome log səviyyəsini azaltmaq
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bot aşkarlanmasını azaltmaq
    options.add_argument("--window-size=1920,1080")  # Pəncərə ölçüsü

    # ChromeDriver-i avtomatik yüklə və quraşdır
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver

def main():
    # ChromeDriver setup
    driver = setup_driver()

    # M3U8 linkini tap
    m3u8_link = get_m3u8_from_network(driver)

    # Link tapıldısa fayl yaradılacaq
    if m3u8_link:
        with open(CONFIG["log_file"], "w") as file:
            file.write(m3u8_link)
        logging.info(f"M3U8 linki fayla yazıldı: {CONFIG['log_file']}")
    else:
        logging.warning("M3U8 linki tapılmadı, fayl yaradılmadı.")

    # ChromeDriver-ı bağla
    driver.quit()

if __name__ == "__main__":
    main()
