import requests
import m3u8
import os
from github import Github

def fetch_m3u8_stream(url):
    """YouTube linkindən M3U8 faylını alır"""
    response = requests.get(url)
    if response.status_code == 200:
        m3u8_url = response.url  # YouTube canlı yayımının M3U8 linkini alır
        return m3u8_url
    else:
        return None

def upload_to_github(file_path, repo_name, token):
    """Faylı GitHub repozitoriyasına yükləyir"""
    g = Github(token)
    repo = g.get_repo(repo_name)
    with open(file_path, 'r') as file:
        content = file.read()
    repo.create_file(file_path, "Upload M3U8 stream", content)

# Test: YouTube canlı yayım linki ilə işləyin
youtube_url = "https://www.youtube.com/watch?v=ouuCjEjyKVI"
m3u8_stream = fetch_m3u8_stream(youtube_url)
if m3u8_stream:
    with open("stream.m3u8", "w") as f:
        f.write(m3u8_stream)

    # GitHub-a yüklə
    upload_to_github("stream.m3u8", "by-kerimoff/YouTube-Stream-M3U8", "your_github_token_here")
