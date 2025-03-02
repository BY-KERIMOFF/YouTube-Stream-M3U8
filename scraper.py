from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Chrome options
chrome_options = webdriver.ChromeOptions()

# İstəyirsinizsə, headless modunda işləyə bilər
chrome_options.add_argument("--headless")

# Chromedriver-ı avtomatik yükləyin və başlatın
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL-ə get edin (istədiyiniz linki buraya daxil edin)
driver.get("https://www.youtube.com")

# Sayfa yükləndikdən sonra müəyyən bir müddət gözləyin (məsələn 5 saniyə)
time.sleep(5)

# Məsələn, YouTube-da bəzi elementləri tapmaq:
# driver.find_element(By.XPATH, "element_xpath").click()

# Brauzeri bağlayın
driver.quit()
