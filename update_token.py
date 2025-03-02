import re
import requests
from bs4 import BeautifulSoup

# URL-ni uyğun olaraq dəyişin
url = 'https://www.ecanlitvizle.app/xezer-tv-canli-izle/'

# Saytdan məlumatları alırıq
response = requests.get(url)

# Cavabın düzgünlüyünü yoxlayaq
if response.status_code == 200:
    html_content = response.text

    # HTML məzmununu BeautifulSoup ilə analiz edirik
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # URL-ləri tapmaq üçün bütün <a> etiketlərini seçirik
    links = soup.find_all('a', href=True)

    # Hər bir linki yoxlayaq
    old_token_found = False
    for link in links:
        # URL-lərdə tkn= olduğunu tapmağa çalışırıq
        old_token_match = re.search(r'tkn=([A-Za-z0-9_-]+)', link['href'])
        
        if old_token_match:
            old_token = old_token_match.group(1)
            print(f"Köhnə token tapıldı: {old_token}")
            
            # Yeni token əlavə edirik
            new_token = "NEW_TOKEN_HERE"  # Burada yeni token-i tapmalısınız
            new_link = link['href'].replace(old_token, new_token)
            print(f"Yeni link: {new_link}")

            # Yeni linki faylda yazın
            with open("tv.txt", "w") as f:
                f.write(new_link)
            print("Yeni link tv.txt faylında yazıldı!")
            
            old_token_found = True
            break

    if not old_token_found:
        print("Köhnə token tapılmadı.")
        # Token tapılmadıqda boş fayl yazın
        with open("tv.txt", "w") as f:
            f.write("No token found!")
        print("Heç bir token tapılmadı, boş məlumat tv.txt faylında saxlanıldı.")
else:
    print("Saytla əlaqə qurulmadı.")
    with open("tv.txt", "w") as f:
        f.write("Failed to fetch URL")
    print("Saytla əlaqə qurulmadı, səhv mesajı tv.txt faylında saxlanıldı.")
