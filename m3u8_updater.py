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
    "url": "https://yoda.az",  # Kanalların siyahısını almaq üçün URL
    "wait_time": 30,  # Sayt yüklənməsi üçün gözləmə vaxtı (saniyə)
    "log_file": "yoda_channels.txt",  # Linklərin yazılacağı fayl adı
}

# Logging konfiqurasiyası
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})

    # ChromeDriver-i avtomatik yüklə və quraşdır
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(CONFIG["wait_time"])
    return driver


def get_all_channel_links(driver):
    """
    Yoda.az saytından bütün kanalların `.m3u8` linklərini tapır.
    """
    try:
        driver.get(CONFIG["url"])
        logging.info(f"Səhifə yükləndi: {CONFIG['url']}")

        # Kanalların yüklənməsi üçün gözləyin
        time.sleep(10)  # JavaScript-dən elementləri yükləmək üçün vaxt verin

        # Şəbəkə loglarını oxuyun
        logs = driver.get_log("performance")
        m3u8_links = set()  # Unikal linkləri saxlamaq üçün set istifadə edilir

        for entry in logs:
            log = json.loads(entry["message"])
            if "method" in log and log["method"] == "Network.responseReceived":
                url = log["params"]["response"]["url"]
                if ".m3u8" in url:
                    logging.info(f"Şəbəkə loglarından M3U8 linki tapıldı: {url}")
                    m3u8_links.add(url)

        if m3u8_links:
            logging.info(f"Toplam {len(m3u8_links)} M3U8 linki tapıldı.")
        else:
            logging.warning("Heç bir M3U8 linki tapılmadı.")

        return list(m3u8_links)

    except Exception as e:
        logging.error(f"M3U8 linklərini əldə edilərkən xəta: {e}")
        return []


def update_m3u8_links_if_changed(new_links, file_path):
    """
    Yeni linklər varsa, .txt faylını güncəlləyir.
    """
    try:
        # Eski linkləri oxu
        try:
            with open(file_path, "r") as file:
                old_links = [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            old_links = []

        # Yeni linklər ilə müqayisə et
        if set(new_links) != set(old_links):
            logging.info("Linklər dəyişib, fayl güncəllənir.")
            with open(file_path, "w") as file:
                for link in new_links:
                    file.write(link + "\n")
            return True
        else:
            logging.info("Linklər dəyişmir, fayl aktualdır.")
            return False

    except Exception as e:
        logging.error(f"Fayl güncəllənilərkən xəta: {e}")
        return False


def main():
    """
    Ana funksiya: Bütün kanalların `.m3u8` linklərini tapır və `.txt` faylına yazır.
    """
    # ChromeDriver setup
    driver = setup_driver()

    # Bütün kanalların `.m3u8` linklərini tap
    m3u8_links = get_all_channel_links(driver)

    # Linklər tapıldısa fayl yaradılacaq
    if m3u8_links:
        updated = update_m3u8_links_if_changed(m3u8_links, CONFIG["log_file"])
        if updated:
            logging.info(f"{len(m3u8_links)} M3U8 linki fayla yazıldı: {CONFIG['log_file']}")
    else:
        logging.warning("Heç bir M3U8 linki tapılmadı, fayl boşdur.")

    # ChromeDriver-ı bağla
    driver.quit()


if __name__ == "__main__":
    main()
