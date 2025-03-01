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
    "iframe_wait_time": 20,  # Iframe üçün gözləmə vaxtı (saniyə)
    "video_wait_time": 30,  # Video elementinə baxmaq üçün gözləmə vaxtı (saniyə)
    "log_file": "m3u8_link.txt",  # M3U8 linkinin yazılacağı fayl adı
}

# Logging konfiqurasiyası
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_m3u8_from_network_logs(driver):
    """
    Şəbəkə loglarından M3U8 linkini axtarır.
    """
    try:
        logs = driver.get_log("performance")
        for entry in logs:
            log = json.loads(entry["message"])
            if "method" in log and log["method"] == "Network.responseReceived":
                url = log["params"]["response"]["url"]
                if "m3u8" in url:
                    logging.info(f"Şəbəkə loglarından M3U8 linki tapıldı: {url}")
                    return url
        logging.warning("Şəbəkə loglarında M3U8 linki tapılmadı.")
        return None
    except Exception as e:
        logging.error(f"Şəbəkə loglarının analizində xəta: {e}")
        return None


def get_m3u8_from_network(driver):
    """
    Selenium vasitəsiylə M3U8 linkini tapır.
    """
    try:
        driver.get(CONFIG["url"])
        logging.info(f"Səhifə yükləndi: {CONFIG['url']}")

        # Iframe varsa, ona keçid edir
        try:
            WebDriverWait(driver, CONFIG["iframe_wait_time"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                driver.switch_to.frame(iframes[0])
                logging.info("Iframe-ə keçid edildi.")
        except Exception as e:
            logging.warning("Iframe tapılmadı, doğrudan video elementinə keçilir.")

        # Video elementini gözləyir
        try:
            WebDriverWait(driver, CONFIG["video_wait_time"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            logging.info("Video elementi tapıldı.")
        except Exception as e:
            logging.warning("Video elementi tapılmadı, şəbəkə loglarından axtarılır.")

        # Video elementinin src atributunu əldə edir
        m3u8_link = None
        try:
            video_element = driver.find_element(By.TAG_NAME, "video")
            m3u8_link = video_element.get_attribute("src")
            if m3u8_link and m3u8_link.startswith("blob:"):
                logging.info("Blob linki tapıldı. Şəbəkə logları təhlil edilir...")
                m3u8_link = get_m3u8_from_network_logs(driver)
        except Exception as e:
            logging.error(f"Video elementindən M3U8 linki əldə edilərkən xəta: {e}")

        if m3u8_link:
            logging.info(f"M3U8 linki tapıldı: {m3u8_link}")
            return m3u8_link

        logging.warning("M3U8 linki tapılmadı.")
        return None

    except Exception as e:
        logging.error(f"M3U8 linki əldə edilərkən xəta: {e}")
        return None


def setup_driver():
    """
    ChromeDriver-ı quraşdırır və başsız rejimdə başlatır.
    """
    options = Options()
    options.add_argument("--headless")  # Başsız rejim
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")  # Chrome log səviyyəsini azaltmaq
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bot aşkarlanmasını azaltmaq
    options.add_argument("--window-size=1920,1080")  # Pəncərə ölçüsü
    options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})  # Şəbəkə loglarını aktivləşdir

    # ChromeDriver-i avtomatik yüklə və quraşdır
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver


def main():
    """
    Ana funksiya: M3U8 linkini tapır və `.txt` faylına yazır.
    """
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
