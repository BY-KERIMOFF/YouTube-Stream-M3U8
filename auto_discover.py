#!/usr/bin/env python3
"""
YouTube-dan avtomatik canlı yayın kəşfiyyatçısı
✨ By_Kerimoff ✨
"""

import requests
import re
import json
import time
import os
from datetime import datetime
from urllib.parse import quote

class YouTubeAutoDiscover:
    def __init__(self):
        self.data_dir = "data"
        self.setup_directories()
        
    def setup_directories(self):
        """Qovluqları yaradır"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs("public", exist_ok=True)
    
    def get_trending_keywords(self):
        """Trend olan açar sözləri alır"""
        trends = [
            "canlı yayın", "live stream", "tv canlı", "canlı tv",
            "spor canlı", "haber canlı", "müzik canlı", "film canlı",
            "belgesel canlı", "dizi canlı", "news live", "sports live",
            "music live", "türk kanalları", "türk tv", "turkey live"
        ]
        return trends
    
    def search_youtube_live(self, query):
        """YouTube-da canlı yayın axtarır"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Video ID-ləri tap
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
            unique_ids = list(dict.fromkeys(video_ids))[:10]  # İlk 10 unikal ID
            
            live_streams = []
            for video_id in unique_ids:
                stream_info = self.get_stream_info(video_id)
                if stream_info and stream_info.get('is_live'):
                    live_streams.append(stream_info)
                    print(f"✅ Canlı yayın tapıldı: {stream_info['title']}")
                
                # 1 saniyə gözlə ki, YouTube bloklamasın
                time.sleep(1)
            
            return live_streams
            
        except Exception as e:
            print(f"❌ Axtarış xətası '{query}': {str(e)}")
            return []
    
    def get_stream_info(self, video_id):
        """Video məlumatlarını alır"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # yt-dlp ilə məlumat al
            import subprocess
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '--skip-download',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                return {
                    'video_id': video_id,
                    'title': data.get('title', 'Bilinməyən'),
                    'channel': data.get('uploader', 'Bilinməyən'),
                    'is_live': data.get('is_live', False),
                    'view_count': data.get('concurrent_view_count', 0),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': data.get('thumbnail', ''),
                    'discovered_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"⚠️ Video məlumatı alınmadı {video_id}: {str(e)}")
        
        return None
    
    def get_stream_url(self, video_id):
        """Canlı yayın URL-ni alır"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best[height<=720]',
                '--no-warnings',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url and stream_url.startswith('http'):
                    return stream_url
                    
        except Exception as e:
            print(f"❌ Stream URL alınmadı {video_id}: {str(e)}")
        
        return None
    
    def discover_live_streams(self):
        """Bütün canlı yayınları kəşf et"""
        print("🔍 YouTube-da canlı yayınlar kəşf edilir...")
        
        all_live_streams = []
        keywords = self.get_trending_keywords()
        
        for keyword in keywords:
            print(f"🔎 Axtarılır: '{keyword}'")
            streams = self.search_youtube_live(keyword)
            all_live_streams.extend(streams)
            
            # 2 saniyə gözlə ki, YouTube bloklamasın
            time.sleep(2)
        
        # Təkrar elementləri sil
        unique_streams = []
        seen_ids = set()
        
        for stream in all_live_streams:
            if stream['video_id'] not in seen_ids:
                unique_streams.append(stream)
                seen_ids.add(stream['video_id'])
        
        print(f"🎯 Ümumi tapılan canlı yayınlar: {len(unique_streams)}")
        
        # Fayla yaz
        self.save_discovered_streams(unique_streams)
        return unique_streams
    
    def save_discovered_streams(self, streams):
        """Kəşf edilən yayınları fayla yaz"""
        data = {
            'last_update': datetime.now().isoformat(),
            'total_streams': len(streams),
            'streams': streams
        }
        
        with open(f"{self.data_dir}/discovered_channels.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 {len(streams)} canlı yayın qeydə alındı")

def main():
    print("🚀 YouTube Auto Discover başladı...")
    discover = YouTubeAutoDiscover()
    streams = discover.discover_live_streams()
    print(f"✅ Kəşfiyyat tamamlandı: {len(streams)} canlı yayın")

if __name__ == "__main__":
    main()
