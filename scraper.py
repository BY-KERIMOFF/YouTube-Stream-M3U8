from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Chrome üçün webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Brauzeri görünməz edirik
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# WebDriver konfiqurasiyası
service = Service('path_to_your_chromedriver')  # ChromeDriver yolunu göstərin
driver = webdriver.Chrome(service=service, options=chrome_options)

# M3U linklərini tapmaq üçün URL-lər
urls = [
    "https://www.ecanlitvizle.app/xezer-tv-canli-izle/",
    "https://www.ecanlitvizle.app/show-tv-canli-izle-hd-4/",
    "https://www.ecanlitvizle.app/tlc-tv-canli/"
]

# M3U linklərini tapmaq və yazmaq üçün fayl
output_path = 'm3u_links.txt'

with open(output_path, 'w', encoding='utf-8') as file:
    # URL-ləri dövr edirik
    for url in urls:
        driver.get(url)  # Saytı yükləyirik
        time.sleep(5)  # Saytın tam yüklənməsi üçün bir neçə saniyə gözləyirik

        # Saytın HTML-i ilə işləyirik
        links = driver.find_elements(By.TAG_NAME, 'a')  # Bütün <a> tag-larını tapırıq

        for link in links:
            href = link.get_attribute('href')
            if '.m3u' in href:  # Yalnız M3U linklərini tapırıq
                file.write(f'{href}\n')  # M3U linkini fayla yazırıq

driver.quit()  # WebDriver-i bağlayırıq
print(f'M3U linkləri {output_path} faylına yazıldı.')
