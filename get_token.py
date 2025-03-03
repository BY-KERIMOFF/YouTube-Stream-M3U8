from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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

# Gözlənilən elementə çatırıq və tokeni alırıq
element = driver.find_element("xpath", "//script[contains(text(),'tkn=')]")
# Elementdən tokeni çıxarırıq
token = element.text.split("tkn=")[1].split("&")[0]
print(f"Tapılan token: {token}")

# Tokeni fayla yazırıq
with open("token.txt", "w") as f:
    f.write(token)

# Driver-i bağlayırıq
driver.quit()
