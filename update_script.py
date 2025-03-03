import requests

# URL tərtib et
url = 'https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=XdBMwsPAdMN_l8EqNmVx5A&tms=1740980749'

# Sorğu başlıqları
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Referer': 'https://www.ecanlitvizle.app/',
    'Origin': 'https://www.ecanlitvizle.app'
}

# GET sorğusu göndər
response = requests.get(url, headers=headers)

# Cavabı yoxla
if response.status_code == 200:
    print("✅ Sorğu uğurlu oldu.")
    
    # Cavab məzmununu fayla yaz
    with open("stream.m3u8", "w") as file:
        file.write(response.text)
    print("✅ stream.m3u8 faylı yeniləndi.")
else:
    print(f"❌ Sorğu uğursuz oldu. Status kodu: {response.status_code}")
