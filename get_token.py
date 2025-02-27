from github import Github  # Düzgün kitabxana idxalı
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Chrome setup
chrome_binary_path = "/usr/bin/chromium-browser"  # Chrome yolu
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = chrome_binary_path

service = Service(executable_path='/usr/local/bin/chromedriver')  # Chromedriver yolu

# Browser işə salınır
driver = webdriver.Chrome(service=service, options=chrome_options)

# Tokeni tapmaq
def get_new_token():
    driver.get("https://str.yodacdn.net/ictimai/tracks-v1a1/mono.ts.m3u8?token=e94ce96ed0bb56a38653e3258d32bddd4800a6be-866797cc0d6dbea82bcd1353aa390e56-1740700536-1740689736")
    time.sleep(5)  # Sayfanın yüklənməsi üçün vaxt

    # Tokeni tapmaq üçün XPath yoxlanmalı
    try:
        token_element = driver.find_element(By.XPATH, "//*[contains(text(),'token')]")  # XPath dəyişdirildi
        token = token_element.text
        return token
    except Exception as e:
        print(f"Token tapılmadı: {e}")
        return None

# Tokeni alırıq
token = get_new_token()
if token:
    print(f"Alınan token: {token}")
else:
    print("Token tapılmadı!")

# GitHub reposuna link əlavə etmək
def update_github_repo(token):
    github_token = 'YOUR_GITHUB_TOKEN'  # GitHub Token
    repo_name = 'by-kerimoff/YouTube-Stream-M3U8'  # Repo adı

    # GitHub ilə əlaqə
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    
    # M3U8 linki əlavə edirik
    file_path = "m3u8_links.txt"  # Fayl adı
    content = f"Token: {token}\nM3U8 Link: https://str.yodacdn.net/ictimai/tracks-v1a1/mono.ts.m3u8?token={token}\n"

    try:
        # Fayl varsa, onu yeniləyirik
        file = repo.get_contents(file_path)
        repo.update_file(file_path, "Added new m3u8 link", content, file.sha)
    except:
        # Fayl yoxdursa, yeni fayl əlavə edirik
        repo.create_file(file_path, "Added new m3u8 link", content)

# GitHub-a əlavə
if token:
    update_github_repo(token)

# Browserı bağlayırıq
driver.quit()
