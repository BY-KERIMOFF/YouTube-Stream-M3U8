import requests
import re

# Verilən linki daxil edirik
url = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=JbZLksnwCGdDPy9ojcvXCQ&tms=1740960891"

# Tokeni regex ilə tapırıq
match = re.search(r'tkn=([a-zA-Z0-9]+)', url)
if match:
    old_token = match.group(1)
    print(f"Köhnə token tapıldı: {old_token}")
else:
    print("Köhnə token tapılmadı.")
    exit()

# Yeni tokeni daxil et
new_token = "NEW_TOKEN_HERE"  # Buraya yeni tokeni daxil et

# URL-dəki köhnə tokeni yeni token ilə əvəz edirik
new_url = url.replace(old_token, new_token)

print(f"Yeni URL: {new_url}")

# tv.txt faylını yazırıq
with open('tv.txt', 'w') as file:
    file.write(new_url)

print("Yeni link tv.txt faylında yazıldı!")
