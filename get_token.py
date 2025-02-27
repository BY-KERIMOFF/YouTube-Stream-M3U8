import requests

# GitHub Personal Access Token
github_token = 'YOUR_GITHUB_TOKEN'  
repo_name = 'by-kerimoff/YouTube-Stream-M3U8'
file_path = 'm3u8_links.txt' 

# Yeni link
content = f"Token: {token}\nM3U8 Link: https://str.yodacdn.net/ictimai/tracks-v1a1/mono.ts.m3u8?token={token}\n"

# GitHub API URL
url = f'https://api.github.com/repos/{repo_name}/contents/{file_path}'

# Başlıq və məlumatlar
headers = {
    'Authorization': f'token {github_token}',
    'Content-Type': 'application/json',
}

# GitHub API ilə əlaqə qururuq
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Fayl varsa, onu yeniləyirik
    sha = response.json()['sha']
    data = {
        'message': 'Added new m3u8 link',
        'content': content.encode('utf-8').decode('utf-8'),
        'sha': sha,
    }
    response = requests.put(url, json=data, headers=headers)
else:
    # Fayl yoxdursa, yeni fayl əlavə edirik
    data = {
        'message': 'Added new m3u8 link',
        'content': content.encode('utf-8').decode('utf-8'),
    }
    response = requests.put(url, json=data, headers=headers)

print(response.json())
