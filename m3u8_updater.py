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
    "iframe_wait_time": 30,  # Iframe üçün gözləmə vaxtı (saniyə)
    "video_wait_time": 60,  # Video elementinə baxmaq üçün gözləmə vaxtı (saniyə)
    "log_file": "m3u8_links.txt",  # M3U8 linklərinin yazılacağı fayl adı
}

# Logging konfiqurasiyası
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_m3u8_links_from_network_logs(driver):
    """
    Şəbəkə loglarından bütün .m3u8 linklərini axtarır.
    """
    try:
        logs = driver.get_log("performance")
        m3u8_links = set()  # Unikal linkləri saxlamaq üçün set istifadə edilir
        for entry in logs:
            log = json.loads(entry["message"])
            if "method" in log and log["method"] == "Network.responseReceived":
                url = log["params"]["response"]["url"]
                if "m3u8" in url:
                    logging.info(f"Şəbəkə loglarından M3U8 linki tapıldı: {url}")
                    m3u8_links.add(url)  # Linkləri unikal olaraq əlavə edirik
        if m3u8_links:
            logging.info(f"Toplam {len(m3u8_links)} M3U8 linki tapıldı.")
        else:
            logging.warning("M3U8 linki tapılmadı.")
        return list(m3u8_links)
    except Exception as e:
        logging.error(f"Şəbəkə loglarının analizində xəta: {e}")
        return []


def get_m3u8_link_from_javascript(driver):
    """
    JavaScript-dən M3U8 linkini axtarır.
    """
    try:
        script = """
        const scripts = document.querySelectorAll('script');
        let m3u8Link = null;
        scripts.forEach(script => {
            const text = script.textContent;
            if (text.includes('.m3u8')) {
                const match = text.match(/(http.*\.m3u8)/);
                if (match) {
                    m3u8Link = match[0];
                }
            }
        });
        return m3u8Link;
        """
        m3u8_link = driver.execute_script(script)
        if m3u8_link:
            logging.info(f"JavaScript-dən M3U8 linki tapıldı: {m3u8_link}")
            return m3u8_link
        else:
            logging.warning("JavaScript-də M3U8 linki tapılmadı.")
            return None
    except Exception as e:
        logging.error(f"JavaScript-dən M3U8 linkini əldə edilərkən xəta: {e}")
        return None


def get_m3u8_links_from_network(driver):
    """
    Selenium vasitəsiylə bütün M3U8 linklərini tapır.
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
            logging.warning("Video elementi tapılmadı, yalnız şəbəkə loglarından axtarılır.")

        # Şəbəkə loglarından bütün .m3u8 linklərini axtar
        m3u8_links = get_m3u8_links_from_network_logs(driver)

        # Video elementi yoxdursa, JavaScript-dən axtar
        if not m3u8_links:
            m3u8_link = get_m3u8_link_from_javascript(driver)
            if m3u8_link:
                m3u8_links.append(m3u8_link)

        if m3u8_links:
            logging.info(f"{len(m3u8_links)} M3U8 linki tapıldı.")
            return m3u8_links

        logging.warning("Heç bir M3U8 linki tapılmadı.")
        return []

    except Exception as e:
        logging.error(f"M3U8 linklərini əldə edilərkən xəta: {e}")
        return []


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
    driver.set_page_load_timeout(30)
    return driver


def update_m3u8_link_if_changed(new_links, file_path):
    """
    Yeni linklər varsa, .txt faylını güncəlləyir.
    """
    try:
        # Eski linkləri oxu
        with open(file_path, "r") as file:
            old_links = [line.strip() for line in file.readlines()]

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
    except FileNotFoundError:
        logging.info("Fayl tapılmadı, yeni linklər fayla yazılmışdır.")
        with open(file_path, "w") as file:
            for link in new_links:
                file.write(link + "\n")
        return True
    except Exception as e:
        logging.error(f"Fayl güncəllənilərkən xəta: {e}")
        return False


def main():
    """
    Ana funksiya: Bütün M3U8 linklərini tapır və `.txt` faylına yazır.
    """
    # ChromeDriver setup
    driver = setup_driver()

    # Bütün M3U8 linklərini tap
    m3u8_links = get_m3u8_links_from_network(driver)

    # Linklər tapıldısa fayl yaradılacaq
    if m3u8_links:
        updated = update_m3u8_link_if_changed(m3u8_links, CONFIG["log_file"])
        if updated:
            logging.info(f"{len(m3u8_links)} M3U8 linki fayla yazıldı: {CONFIG['log_file']}")
    else:
        logging.warning("Heç bir M3U8 linki tapılmadı, fayl boşdur.")

    # ChromeDriver-ı bağla
    driver.quit()


if __name__ == "__main__":
    main()
