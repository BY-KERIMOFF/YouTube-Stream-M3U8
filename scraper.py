import requests
import re

# URL-dəki tokeni çəkmək
url = "https://ecanlitv3.etvserver.com/xazartv.m3u8?tkn=Fh2F2HhcbuZaxDX8hYPQqQ&tms=1740960002"
response = requests.get(url)

# Tokeni tapmaq (əgər URL-dəki token dəyişirsə)
new_token = re.search(r'tkn=([^&]+)', response.url)
if new_token:
    new_token = new_token.group(1)
    # Tokeni fayla yazmaq
    with open("new_token.txt", "w") as file:
        file.write(new_token)
else:
    print("Token tapılmadı")
