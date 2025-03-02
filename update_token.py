import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

# Selenium ilə Chrome'u başlat
options = Options()
options.headless = True  # Başsız rejimdə işləsin
service = Service(executable_path="/path/to/chromedriver")  # chromedriver yolunu daxil et
driver = webdriver.Chrome(service=service, options=options)

# Sayta gedək
url = "https://www.ecanlitvizle.app/kucukcekmece-mobese-canli-izle/"
driver.get(url)

# Saytın yüklənməsini gözləyək
time.sleep(5)

# Saytın HTML məzmununu əldə et
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")

# Tokeni tapmaq üçün müvafiq HTML elementini tap
token_pattern = r'tkn=([a-zA-Z0-9]+)'
token_match = re.search(token_pattern, page_source)

if token_match:
    token = token_match.group(1)
    print(f"Köhnə token tapıldı: {token}")

    # Yeni token tapıldısa, onu tv.txt faylında qeyd edirik
    new_token = "NEW_TOKEN_HERE"  # Burada yeni token tapılacaq, lazım gələrsə skripti tənzimləyin
    new_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={new_token}&tms=1740960002"

    with open("tv.txt", "w") as file:
        file.write(new_url)
    print(f"Yeni token: {new_token}")
    print(f"Yeni link: {new_url}")
else:
    print("Token tapılmadı")

# Brauzeri bağla
driver.quit()
