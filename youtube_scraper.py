#!/usr/bin/env python3
"""
GitHub Actions üçün YouTube M3U Generator
✨ By_Kerimoff ✨
"""

import os
import json
import requests
import subprocess
import re
from datetime import datetime
import time

class YouTubeM3UGenerator:
    def __init__(self):
        self.tokens_file = "data/tokens.txt"
        self.channels_file = "data/channels.json"
        self.output_dir = "output"
        self.public_dir = "public"
        
        # Əsas kanallar
        self.default_channels = [
            {"name": "SHOW TV", "id": "KpA64R5Jg-4"},
            {"name": "HABERTÜRK TV", "id": "qEQu1Z4Xl_4"},
            {"name": "CNN TÜRK", "id": "0TQZLK4kKcI"},
            {"name": "TRT 1", "id": "YLp6lnytp8I"},
            {"name": "KANAL D", "id": "gJrVMiKMSkY"},
            {"name": "TV8", "id": "6MvJ_gbGg_s"},
            {"name": "STAR TV", "id": "Y1K3y8R0u4M"},
            {"name": "FOX TV", "id": "4t_3s02XeXo"},
            {"name": "ATV", "id": "3uU6E7xYd_4"},
            {"name": "TGRT HABER", "id": "7T7tW7X7T7T"},
            {"name": "NTV", "id": "0MFB2X3jC7E"},
            {"name": "TRT SPOR", "id": "k4t1t7Vq8h8"},
            {"name": "BEIN SPORTS 1", "id": "6MvJ_gbGg_s"},
            {"name": "BEIN SPORTS 2", "id": "Y1K3y8R0u4M"},
            {"name": "A HABER", "id": "4t_3s02XeXo"}
        ]
        
        self.setup_directories()
    
    def setup_directories(self):
        """Qovluqları yaradır"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.public_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)
    
    def load_tokens(self):
        """YouTube tokenlarını yükləyir"""
        tokens = []
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'r') as f:
                tokens = [line.strip() for line in f if line.strip()]
        return tokens
    
    def load_custom_channels(self):
        """Xüsusi kanalları yükləyir"""
        if os.path.exists(self.channels_file):
            with open(self.channels_file, 'r') as f:
                return json.load(f)
        return []
    
    def get_live_stream_url(self, video_id):
        """YouTube canlı yayın URL-ni alır"""
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best[height<=720]',
                '--no-warnings',
                '--socket-timeout', '10',
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url and stream_url.startswith('http'):
                    return stream_url
                    
        except Exception as e:
            print(f"⚠️ {video_id} üçün xəta: {str(e)}")
        
        return None
    
    def search_live_channels(self, query):
        """YouTube-da canlı kanalları axtarır"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={query}+canlı"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
                unique_ids = list(dict.fromkeys(video_ids))[:5]
                
                live_channels = []
                for video_id in unique_ids:
                    stream_url = self.get_live_stream_url(video_id)
                    if stream_url:
                        live_channels.append({
                            'video_id': video_id,
                            'name': f"{query} Canlı",
                            'stream_url': stream_url
                        })
                        if len(live_channels) >= 3:
                            break
                
                return live_channels
                
        except Exception as e:
            print(f"⚠️ Axtarış xətası: {str(e)}")
        
        return []
    
    def generate_m3u_playlist(self):
        """M3U playlist yaradır"""
        print("🎥 M3U playlist yaradılır...")
        
        all_channels = []
        
        # 1. Əsas kanalları əlavə et
        print("📺 Əsas kanallar yoxlanılır...")
        for channel in self.default_channels:
            stream_url = self.get_live_stream_url(channel['id'])
            if stream_url:
                all_channels.append({
                    'name': channel['name'],
                    'url': stream_url
                })
                print(f"✅ {channel['name']}")
            else:
                print(f"❌ {channel['name']} - Canlı yayın yoxdur")
        
        # 2. Xüsusi kanalları əlavə et
        custom_channels = self.load_custom_channels()
        for channel in custom_channels:
            stream_url = self.get_live_stream_url(channel.get('id', ''))
            if stream_url:
                all_channels.append({
                    'name': channel.get('name', 'Bilinməyən'),
                    'url': stream_url
                })
        
        # 3. Tokenlərlə axtarış et
        tokens = self.load_tokens()
        for token in tokens:
            print(f"🔍 '{token}' axtarılır...")
            live_channels = self.search_live_channels(token)
            for channel in live_channels:
                all_channels.append({
                    'name': channel['name'],
                    'url': channel['stream_url']
                })
        
        # 4. M3U faylını yarat
        m3u_content = ['#EXTM3U']
        m3u_content.append('#PLAYLIST:YouTube Canlı Yayınlar')
        m3u_content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        m3u_content.append(f'#TOTAL:{len(all_channels)}')
        m3u_content.append('#AUTO_UPDATE:6 hours')
        m3u_content.append('#BY:Kerimoff')
        
        for channel in all_channels:
            m3u_content.append(f'#EXTINF:-1 tvg-name="{channel["name"]}",{channel["name"]}')
            m3u_content.append(channel['url'])
        
        # 5. Faylları yadda saxla
        output_path = os.path.join(self.output_dir, "playlist.m3u")
        public_path = os.path.join(self.public_dir, "playlist.m3u")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
        
        with open(public_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
        
        print(f"✅ M3U playlist yaradıldı: {len(all_channels)} kanal")
        print(f"📁 Fayl: {public_path}")
        
        return len(all_channels)

def main():
    print("🚀 YouTube M3U Generator başladı...")
    print(f"⏰ Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    generator = YouTubeM3UGenerator()
    channel_count = generator.generate_m3u_playlist()
    
    print(f"🎉 Tamamlandı! {channel_count} kanal əlavə edildi.")
    
    # Status faylı yarat
    status = {
        "last_update": datetime.now().isoformat(),
        "channel_count": channel_count,
        "status": "success"
    }
    
    with open("output/status.json", "w") as f:
        json.dump(status, f, indent=2)

if __name__ == "__main__":
    main()
