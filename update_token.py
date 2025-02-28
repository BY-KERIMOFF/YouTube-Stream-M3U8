import requests
from bs4 import BeautifulSoup

# Səhifə URL-i
url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"

# Səhifəni açırıq
response = requests.get(url)

# HTML-i BeautifulSoup ilə analiz edirik
soup = BeautifulSoup(response.text, 'html.parser')

# Token-i tapmaq üçün müvafiq elementi tapırıq
# Burada tokeni göstərən elementi tapmalısınız (misal olaraq, bu, bir input elementidir)
token = soup.find('input', {'name': 'token'})['value']

# Yeni token ilə URL yaratmaq
new_url = f"https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn={token}&tms=1740712041"

print(new_url)  # Yeni URL-i ekrana yazdırırıq
