import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔎 M3U8 linkini tapmaq üçün network traffic-i yoxlayan funksiya
def get_m3u8_from_network():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
        driver.get(url)

        # Sayfanın yüklənməsini gözləyirik (daha uzun gözləmə müddəti)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

        logs = driver.get_log("performance")
        m3u8_link = None
        print("Network logları:")
        for entry in logs:
            try:
                log = json.loads(entry["message"])["message"]
                if log["method"] == "Network.responseReceived":
                    url = log["params"]["response"]["url"]
                    print(f"Tapılan URL: {url}")  # Logları çap edirik
                    if "xazartv.m3u8" in url:
                        m3u8_link = url
                        break
            except Exception as e:
                print(f"Xəta baş verdi: {e}")
                continue

        driver.quit()
        return m3u8_link
    except Exception as e:
        print(f"Network yaxalama xətası: {e}")
        return None

# 🔄 Tokeni yeniləyən funksiya
def update_token_in_url(url, new_token):
    try:
        if not url:
            return None
        updated_url = re.sub(r"tkn=[^&]*", f"tkn={new_token}", url)
        return updated_url
    except Exception as e:
        print(f"Token yeniləmək xətası: {e}")
        return None

# 🔄 Yerli fayla M3U8 linkini yazan funksiya
def write_to_local_file(m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, fayl yenilənmədi."

    try:
        # Yeni məzmunu hazırlayırıq
        new_content = f"#EXTM3U\n#EXTINF:-1,xezer tv\n{m3u8_link}\n"

        # Yerli fayla yazırıq
        with open("token.txt", "w") as file:
            file.write(new_content)
        print("Yerli fayl uğurla yeniləndi.")
    except Exception as e:
        print(f"Fayla yazma xətası: {e}")
        return f"Fayla yazma xətası: {e}"

# 🔄 Əsas işləyən funksiya
def main():
    # Yeni tokeni daxil et
    new_token = "NrfHQG16Bk4Qp4yo0YWCaQ"  # Yenilənməli olan token

    # Saytdan yeni M3U8 linkini götür
    m3u8_link = get_m3u8_from_network()

    if m3u8_link:
        updated_m3u8_link = update_token_in_url(m3u8_link, new_token)
        print(f"Yeni M3U8 linki: {updated_m3u8_link}")
    else:
        print("M3U8 tapılmadı.")
        return

    # Yerli fayla yaz
    result = write_to_local_file(updated_m3u8_link)
    print(result)

# 🏃‍♂️ Skripti işə sal
if __name__ == "__main__":
    main()
