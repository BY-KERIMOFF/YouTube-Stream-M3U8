from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Başsız rejim
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# ChromeDriver'ın xidmətini qururuq
service = Service(ChromeDriverManager().install())

# WebDriver obyektini yaratmaq
driver = webdriver.Chrome(service=service, options=chrome_options)

# Sayta gedirik
driver.get("https://your-url-here.com")  # URL-ni dəyişdirin

try:
    # Dinamik yükləmə üçün gözləyirik
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//script[contains(text(),'tkn=')]"))
    )
    
    # Elementi tapırıq
    element = driver.find_element(By.XPATH, "//script[contains(text(),'tkn=')]")
    
    # Tokeni alırıq
    token = element.text.split("tkn=")[1].split("&")[0]
    print(f"Tapılan token: {token}")
    
    # Tokeni fayla yazırıq
    with open("token.txt", "w") as f:
        f.write(token)
        
except Exception as e:
    print(f"Error: {str(e)}")

# Driver-i bağlayırıq
driver.quit()
