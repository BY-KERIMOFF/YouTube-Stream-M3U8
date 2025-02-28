import requests

# Tokenli URL
url = "https://live.cdn-canlitv.com/aztv2.m3u8?anahtar=QEoJcC_5a3IVTERXetIwJg&sure=1740723511&ip=185.146.115.168"

def get_new_token():
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Yeni token linki:", response.url)
        return response.url
    else:
        print("Xəta baş verdi, status kodu:", response.status_code)
        return None

# Yeni tokeni alırıq
new_token_url = get_new_token()
