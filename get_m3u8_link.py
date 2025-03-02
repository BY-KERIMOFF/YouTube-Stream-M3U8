import time
import json
import re
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Loglama konfiqurasiyası
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("script.log"),  # Fayla yaz
        logging.StreamHandler()  # Konsola yaz
    ]
)

# Konfiqurasiya faylı
CONFIG_FILE = "config.json"

# Konfiqurasiya faylını oxuyan funksiya
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        logging.info("Konfiqurasiya faylı uğurla yükləndi.")
        return config
    except Exception as e:
        logging.error(f"Konfiqurasiya faylı yüklənərkən xəta: {e}")
        return None

# Email göndərən funksiya
def send_email(subject, body, config):
    try:
        msg = MIMEMultipart()
        msg["From"] = config["email"]["from"]
        msg["To"] = config["email"]["to"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(config["email"]["smtp_server"], config["email"]["smtp_port"])
        server.starttls()
        server.login(config["email"]["from"], config["email"]["password"])
        server.sendmail(config["email"]["from"], config["email"]["to"], msg.as_string())
        server.quit()
        logging.info("Email uğurla göndərildi.")
    except Exception as e:
        logging.error(f"Email göndərilərkən xəta: {e}")

# Verilənlər bazasına yazan funksiya
def save_to_database(m3u8_link, config):
    try:
        conn = sqlite3.connect(config["database"]["path"])
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS m3u8_links (id INTEGER PRIMARY KEY, link TEXT, timestamp DATETIME)")
        cursor.execute("INSERT INTO m3u8_links (link, timestamp) VALUES (?, ?)", (m3u8_link, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        logging.info("M3U8 linki verilənlər bazasına yazıldı.")
    except Exception as e:
        logging.error(f"Verilənlər bazasına yazarkən xəta: {e}")

# API-ə məlumat göndərən funksiya
def send_to_api(m3u8_link, config):
    try:
        response = requests.post(config["api"]["url"], json={"link": m3u8_link})
        if response.status_code == 200:
            logging.info("M3U8 linki API-ə uğurla göndərildi.")
        else:
            logging.error(f"API-ə göndərilərkən xəta: {response.status_code}")
    except Exception as e:
        logging.error(f"API-ə göndərilərkən xəta: {e}")

# 🔎 M3U8 linkini tapmaq üçün network traffic-i yoxlayan funksiya
def get_m3u8_from_network(url, config, retries=3):
    for attempt in range(retries):
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--user-agent={config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')}")
            if "proxy" in config:
                options.add_argument(f"--proxy-server={config['proxy']}")
            options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

            # ChromeDriver-ı avtomatik yüklə və istifadə et
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(url)

            # Sayfanın yüklənməsini gözləyirik
            WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

            # Iframe-ə keçid edirik
            iframe = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)

            # Video elementinin yüklənməsini gözləyirik
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "video")))

            # JavaScript ilə M3U8 linkini tapmağa çalışırıq
            try:
                m3u8_link = driver.execute_script("return document.querySelector('video').src;")
                logging.info(f"JavaScript ilə tapılan M3U8 linki: {m3u8_link}")
            except Exception as e:
                logging.warning(f"JavaScript ilə M3U8 linki tapılmadı: {e}")
                m3u8_link = None

            # Əgər JavaScript ilə tapılmadısa, logları təhlil edirik
            if not m3u8_link:
                logs = driver.get_log("performance")
                logging.info("Network logları təhlil edilir...")
                for entry in logs:
                    try:
                        log = json.loads(entry["message"])  # Log məlumatını JSON formatında oxu
                        if "method" in log and log["method"] == "Network.responseReceived":
                            url = log["params"]["response"]["url"]
                            logging.info(f"Tapılan URL: {url}")
                            if "m3u8" in url:  # M3U8 linkini axtar
                                m3u8_link = url
                                logging.info(f"M3U8 linki tapıldı: {m3u8_link}")
                                break
                    except Exception as e:
                        logging.error(f"Log təhlili zamanı xəta: {e}")
                        continue

            driver.quit()
            return m3u8_link
        except Exception as e:
            logging.error(f"Cəhd {attempt + 1}/{retries} uğursuz oldu: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # 5 saniyə gözlə və yenidən cəhd et
            else:
                logging.error("M3U8 linki tapılmadı.")
                return None

# 🔄 Əsas işləyən funksiya
def main():
    start_time = time.time()
    config = load_config()
    if not config:
        return

    # Birdən çox URL üçün dəstək
    urls = config.get("urls", ["https://www.ecanlitvizle.app/xezer-tv-canli-izle/"])
    for url in urls:
        m3u8_link = get_m3u8_from_network(url, config)
        if m3u8_link:
            updated_m3u8_link = update_token_in_url(m3u8_link, config.get("new_token", "NrfHQG16Bk4Qp4yo0YWCaQ"))
            logging.info(f"Yeni M3U8 linki: {updated_m3u8_link}")
            write_to_local_file(updated_m3u8_link, config.get("output_file", "token.txt"))
            save_to_database(updated_m3u8_link, config)
            send_to_api(updated_m3u8_link, config)
        else:
            logging.error(f"{url} üçün M3U8 tapılmadı.")

    # Email bildirişi
    elapsed_time = time.time() - start_time
    send_email("Skript Tamamlandı", f"Skript uğurla tamamlandı. Müddət: {elapsed_time:.2f} saniyə.", config)

# 🏃‍♂ Skripti işə sal
if __name__ == "__main__":
    main()
