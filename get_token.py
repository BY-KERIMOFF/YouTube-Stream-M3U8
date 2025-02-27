from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# WebDriver istifadə edərək saytı açırıq
def get_new_token():
    # WebDriver yolu (Ubuntu üçün artıq quraşdırılıb)
    driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver')

    # Tokeni əldə etmək üçün səhifə URL-ni daxil edirik
    driver.get("https://example.com")  # Tokeni aldığınız saytın URL-i

    # Sayfanın tam yüklənməsini gözləyirik
    time.sleep(5)  # Sayfanın yüklənməsini gözləyirik

    # Tokeni tapırıq (tokeni tapmaq üçün doğru elementin XPath-ini bilmək lazımdır)
    token_element = driver.find_element(By.XPATH, "//div[@id='token']")  # Tokenin olduğu yeri doğru şəkildə tapın
    token = token_element.text

    driver.quit()  # WebDriver-u bağlayırıq

    return token

# Yeni tokeni alırıq
new_token = get_new_token()

if new_token:
    # Yeni tokenlə linki yaradıb çıxarırıq
    link = f"https://ecanlitv3.etvserver.com/tv8.m3u8?tkn={new_token}&tms=1740695213"
    print(f"Yeni link: {link}")
