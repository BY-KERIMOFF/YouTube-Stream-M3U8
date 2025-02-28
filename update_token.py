from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_m3u8_link():
    # Chrome seçimləri
    options = Options()
    options.add_argument("--headless")  # GUI olmadan işləmək
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # ChromeDriver-i yüklə və başlat
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Sayta daxil ol
    url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"
    driver.get(url)
    
    # Səhifənin tam yüklənməsini gözlə
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        print("Səhifə uğurla yükləndi.")
    except Exception as e:
        print("Səhifə yüklənmədi:", e)
        driver.quit()
        return None
    
    # iframe-i tap və ona keçid et
    try:
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)
        print("Iframe-ə keçid edildi.")
    except Exception as e:
        print("Iframe tapılmadı:", e)
        driver.quit()
        return None
    
    # M3U8 linkini tap
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//video/source[contains(@src, 'm3u8')]")))
        m3u8_element = driver.find_element(By.XPATH, "//video/source[contains(@src, 'm3u8')]")
        m3u8_link = m3u8_element.get_attribute('src')
        print(f"M3U8 linki tapıldı: {m3u8_link}")
    except Exception as e:
        print("M3U8 linki tapılmadı:", e)
        m3u8_link = None
    
    # Brauzeri bağla
    driver.quit()
    return m3u8_link

if __name__ == "__main__":
    m3u8_link = get_m3u8_link()
    if m3u8_link:
        print(f"Tapılan M3U8 linki: {m3u8_link}")
    else:
        print("M3U8 linki tapılmadı.")
