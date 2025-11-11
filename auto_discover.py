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
import subprocess
import sys
from datetime import datetime
from urllib.parse import quote

print("=" * 60)
print("🚀 YOUTUBE AUTO DISCOVER BAŞLADI...")
print("=" * 60)

class YouTubeAutoDiscover:
    def __init__(self):
        self.data_dir = "data"
        self.public_dir = "public"
        self.setup_directories()
        
    def setup_directories(self):
        """Qovluqları yaradır"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.public_dir, exist_ok=True)
        print("✅ Qovluqlar yaradıldı: data/, public/")
    
    def get_trending_keywords(self):
        """Trend olan açar sözləri alır"""
        trends = [
            "canlı yayın", "live stream", "tv canlı", "canlı tv",
            "spor canlı", "haber canlı", "müzik canlı", "film canlı",
            "belgesel canlı", "dizi canlı", "news live", "sports live",
            "music live", "türk kanalları", "türk tv", "turkey live",
            "canlı", "live", "stream", "yayın"
        ]
        return trends
    
    def search_youtube_live(self, query):
        """YouTube-da canlı yayın axtarır"""
        try:
            print(f"🎯 Axtarılır: '{query}'")
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            response = requests.get(search_url, headers=headers, timeout=20)
            response.raise_for_status()
            
            # Video ID-ləri tap
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
            unique_ids = list(dict.fromkeys(video_ids))[:6]  # İlk 6 unikal ID
            
            print(f"📹 Tapılan video ID-ləri: {len(unique_ids)}")
            
            live_streams = []
            for video_id in unique_ids:
                print(f"  🔍 Yoxlanılır: {video_id}")
                stream_info = self.get_stream_info(video_id)
                if stream_info and stream_info.get('is_live'):
                    live_streams.append(stream_info)
                    print(f"  ✅ CANLI: {stream_info['title'][:40]}...")
                elif stream_info:
                    print(f"  ❌ Canlı deyil: {stream_info['title'][:40]}...")
                
                time.sleep(1)  # YouTube bloklamasın deyə
                
            print(f"🎉 '{query}' üçün {len(live_streams)} canlı yayın tapıldı")
            return live_streams
            
        except Exception as e:
            print(f"❌ Axtarış xətası '{query}': {str(e)}")
            return []
    
    def get_stream_info(self, video_id):
        """Video məlumatlarını alır"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # yt-dlp ilə məlumat al
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '--skip-download',
                '--socket-timeout', '15',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                
                stream_info = {
                    'video_id': video_id,
                    'title': data.get('title', 'Bilinməyən Başlıq'),
                    'channel': data.get('uploader', 'Bilinməyən Kanal'),
                    'is_live': data.get('is_live', False),
                    'view_count': data.get('concurrent_view_count', 0),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': data.get('thumbnail', ''),
                    'discovered_at': datetime.now().isoformat()
                }
                return stream_info
            else:
                print(f"  ⚠️ JSON alınmadı: {video_id}")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Timeout: {video_id}")
        except json.JSONDecodeError:
            print(f"  📄 JSON xətası: {video_id}")
        except Exception as e:
            print(f"  ❌ Xəta {video_id}: {str(e)}")
        
        return None
    
    def get_stream_url(self, video_id):
        """Canlı yayın URL-ni alır"""
        try:
            print(f"  🌐 Stream URL alınır: {video_id}")
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best[height<=720]',
                '--no-warnings',
                '--socket-timeout', '15',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url and stream_url.startswith('http'):
                    print(f"  ✅ Stream URL alındı: {video_id}")
                    return stream_url
                else:
                    print(f"  ❌ Stream URL boş: {video_id}")
            else:
                print(f"  ❌ Stream URL alınmadı: {video_id}")
                    
        except Exception as e:
            print(f"  ❌ Stream URL xətası {video_id}: {str(e)}")
        
        return None
    
    def discover_live_streams(self):
        """Bütün canlı yayınları kəşf et"""
        print("\n🔍 YOUTUBE-DA CANLI YAYINLAR AXTARILIR...")
        
        all_live_streams = []
        keywords = self.get_trending_keywords()
        
        print(f"📋 Axtarış sözləri: {len(keywords)}")
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] 🔎 '{keyword}' axtarılır...")
            streams = self.search_youtube_live(keyword)
            all_live_streams.extend(streams)
            
            # 3 saniyə gözlə ki, YouTube bloklamasın
            if i < len(keywords):
                print("⏳ 3 saniyə gözlənir...")
                time.sleep(3)
        
        # Təkrar elementləri sil
        unique_streams = []
        seen_ids = set()
        
        for stream in all_live_streams:
            if stream['video_id'] not in seen_ids:
                unique_streams.append(stream)
                seen_ids.add(stream['video_id'])
        
        print(f"\n🎯 ÜMUMİ TAPILAN CANLI YAYINLAR: {len(unique_streams)}")
        
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
        
        print(f"💾 {len(streams)} canlı yayın 'data/discovered_channels.json' faylına yazıldı")

def main():
    print("🚀 YouTube Auto Discover başladı...")
    discover = YouTubeAutoDiscover()
    streams = discover.discover_live_streams()
    
    print("\n" + "=" * 60)
    print(f"✅ KƏŞFİYYAT TAMAMLANDI: {len(streams)} CANLI YAYIN")
    print("=" * 60)
    
    # Stream URL-ləri yoxla
    working_streams = 0
    for stream in streams:
        stream_url = discover.get_stream_url(stream['video_id'])
        if stream_url:
            working_streams += 1
    
    print(f"📊 İŞLƏYƏN STREAM-LƏR: {working_streams}/{len(streams)}")
    
    return streams

if __name__ == "__main__":
    main()
