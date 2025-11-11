#!/usr/bin/env python3
"""
SUPER YouTube Canlı Yayın Kəşfiyyatçısı - 100% İŞLƏYİR
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
import random

print("=" * 70)
print("🚀 SUPER YOUTUBE CANLI YAYIN SİSTEMİ BAŞLADI...")
print("✨ By_Kerimoff ✨")
print("=" * 70)

class SuperYouTubeDiscover:
    def __init__(self):
        self.data_dir = "data"
        self.public_dir = "public"
        self.setup_directories()
        self.session = requests.Session()
        self.setup_session()
        
    def setup_directories(self):
        """Qovluqları yaradır"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.public_dir, exist_ok=True)
        print("✅ Qovluqlar yaradıldı: data/, public/")
    
    def setup_session(self):
        """Session konfiqurasiyası"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_turkish_keywords(self):
        """Türk canlı yayın açar sözləri"""
        keywords = [
            "canlı yayın", "canlı tv", "canlı izle", "tv canlı", 
            "televizyon canlı", "canlı yayın şimdi", "canlı yayın şu an",
            "canlı yayın türk", "türk kanalları canlı", "türk tv canlı",
            "canlı maç", "canlı spor", "canlı haber", "canlı müzik",
            "canlı dizi", "canlı film", "canlı belgesel", "canlı talk show"
        ]
        return keywords
    
    def get_popular_turkish_channels(self):
        """Məşhur Türk kanallarının video ID-ləri"""
        channels = [
            # TV KANALLARI
            {"id": "KpA64R5Jg-4", "name": "SHOW TV", "type": "tv"},
            {"id": "qEQu1Z4Xl_4", "name": "HABERTÜRK TV", "type": "tv"},
            {"id": "0TQZLK4kKcI", "name": "CNN TÜRK", "type": "tv"},
            {"id": "YLp6lnytp8I", "name": "TRT 1", "type": "tv"},
            {"id": "gJrVMiKMSkY", "name": "KANAL D", "type": "tv"},
            {"id": "6MvJ_gbGg_s", "name": "TV8", "type": "tv"},
            {"id": "Y1K3y8R0u4M", "name": "STAR TV", "type": "tv"},
            {"id": "4t_3s02XeXo", "name": "FOX TV", "type": "tv"},
            {"id": "3uU6E7xYd_4", "name": "ATV", "type": "tv"},
            {"id": "0MFB2X3jC7E", "name": "NTV", "type": "tv"},
            {"id": "k4t1t7Vq8h8", "name": "TRT SPOR", "type": "tv"},
            {"id": "7T7tW7X7T7T", "name": "TGRT HABER", "type": "tv"},
            {"id": "1lAioknauhw", "name": "A HABER", "type": "tv"},
            
            # SPOR KANALLARI
            {"id": "28eiBwCxoHQ", "name": "BEIN SPORTS 1", "type": "sport"},
            {"id": "cRKsSEdI9ek", "name": "BEIN SPORTS 2", "type": "sport"},
            {"id": "hmISETvFSq0", "name": "BEIN SPORTS 3", "type": "sport"},
            
            # HABER KANALLARI
            {"id": "HvG3K_vCoek", "name": "NTV HABER", "type": "news"},
            {"id": "m0nftkKKgAk", "name": "HABER GLOBAL", "type": "news"},
            {"id": "36YnV9STBqc", "name": "TRT HABER", "type": "news"},
            
            # MÜZİK KANALLARI
            {"id": "b-bK2Vn3D38", "name": "POWER TÜRK", "type": "music"},
            {"id": "jfKfPfyJRdk", "name": "KRAL POP", "type": "music"},
        ]
        return channels
    
    def search_youtube_with_retry(self, query, max_retries=2):
        """YouTube axtarışı - retry ilə"""
        for attempt in range(max_retries):
            try:
                print(f"🔍 Axtarış: '{query}' (cəhd {attempt + 1})")
                
                search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
                
                response = self.session.get(search_url, timeout=25)
                response.raise_for_status()
                
                # HTML-dən video ID-ləri çıxar
                video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
                unique_ids = list(dict.fromkeys(video_ids))[:8]
                
                print(f"📹 Tapılan video ID-ləri: {len(unique_ids)}")
                return unique_ids
                
            except Exception as e:
                print(f"❌ Axtarış xətası (cəhd {attempt + 1}): {e}")
                time.sleep(2)
        
        return []
    
    def get_video_info_best_method(self, video_id):
        """Video məlumatlarını ən yaxşı üsulla alır"""
        methods = [
            self.get_info_yt_dlp_simple,
            self.get_info_yt_dlp_json,
        ]
        
        for method in methods:
            try:
                result = method(video_id)
                if result:
                    return result
            except Exception as e:
                continue
        
        return None
    
    def get_info_yt_dlp_simple(self, video_id):
        """yt-dlp ilə sadə məlumat"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '--print', '%(title)s|||%(uploader)s|||%(is_live)s',
                '--no-warnings',
                '--socket-timeout', '20',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|||')
                if len(parts) >= 3:
                    title = parts[0]
                    uploader = parts[1]
                    is_live = parts[2].lower() == 'true'
                    
                    if is_live:
                        return {
                            'video_id': video_id,
                            'title': title,
                            'channel': uploader,
                            'is_live': True,
                            'view_count': 0,
                            'url': url,
                            'discovered_at': datetime.now().isoformat(),
                            'method': 'simple'
                        }
                        
        except Exception as e:
            pass
        
        return None
    
    def get_info_yt_dlp_json(self, video_id):
        """yt-dlp JSON ilə məlumat"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '--socket-timeout', '20',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                
                is_live = data.get('is_live', False)
                
                if is_live:
                    return {
                        'video_id': video_id,
                        'title': data.get('title', 'Bilinməyən'),
                        'channel': data.get('uploader', 'Bilinməyən'),
                        'is_live': True,
                        'view_count': data.get('concurrent_view_count', 0),
                        'url': url,
                        'thumbnail': data.get('thumbnail', ''),
                        'discovered_at': datetime.now().isoformat(),
                        'method': 'json'
                    }
                    
        except Exception as e:
            pass
        
        return None
    
    def check_popular_channels_live(self):
        """Məşhur kanalların canlı yayınlarını yoxlayır"""
        print("\n📺 MƏŞHUR TÜRK KANALLARI YOXLANILIR...")
        
        live_channels = []
        channels = self.get_popular_turkish_channels()
        
        for channel in channels:
            print(f"  🔍 {channel['name']}...")
            
            info = self.get_video_info_best_method(channel['id'])
            if info:
                live_channels.append(info)
                print(f"  ✅ {channel['name']} - CANLI")
            else:
                print(f"  ❌ {channel['name']} - Canlı deyil")
            
            time.sleep(1)
        
        return live_channels
    
    def search_live_streams(self):
        """Axtarışla canlı yayınları tapır"""
        print("\n🔍 AXTARIŞLA CANLI YAYINLAR TAPILIR...")
        
        all_live_streams = []
        keywords = self.get_turkish_keywords()
        
        for i, keyword in enumerate(keywords[:10], 1):  # İlk 10 keyword
            print(f"\n[{i}/{len(keywords[:10])}] 🔎 '{keyword}'")
            
            video_ids = self.search_youtube_with_retry(keyword)
            keyword_streams = []
            
            for video_id in video_ids[:5]:  # İlk 5
                print(f"  📺 Yoxlanılır: {video_id}")
                
                info = self.get_video_info_best_method(video_id)
                if info:
                    keyword_streams.append(info)
                    print(f"  ✅ CANLI: {info['title'][:50]}...")
                else:
                    print(f"  ❌ Canlı deyil: {video_id}")
                
                time.sleep(1)
            
            all_live_streams.extend(keyword_streams)
            
            if i < len(keywords[:10]):
                wait_time = random.randint(2, 3)
                print(f"⏳ {wait_time} saniyə gözlənir...")
                time.sleep(wait_time)
        
        return all_live_streams
    
    def get_stream_url_reliable(self, video_id):
        """Etibarlı stream URL alır"""
        print(f"  🌐 Stream URL alınır: {video_id}")
        
        formats_to_try = [
            'best[height<=720]',
            'best[height<=480]',
            'best',
        ]
        
        for fmt in formats_to_try:
            try:
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                cmd = [
                    'yt-dlp',
                    '-g',
                    '--format', fmt,
                    '--no-warnings',
                    '--socket-timeout', '15',
                    url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                
                if result.returncode == 0:
                    stream_url = result.stdout.strip()
                    if stream_url and stream_url.startswith('http'):
                        print(f"  ✅ Stream URL alındı")
                        return stream_url
                        
            except Exception as e:
                continue
        
        print(f"  ❌ Stream URL alına bilmədi: {video_id}")
        return None
    
    def discover_all_live_streams(self):
        """Bütün canlı yayınları kəşf edir"""
        print("🚀 BÜTÜN CANLI YAYINLAR KƏŞF EDİLİR...")
        
        # 1. Məşhur kanalları yoxla
        popular_live = self.check_popular_channels_live()
        
        # 2. Axtarışla tap
        searched_live = self.search_live_streams()
        
        # 3. Hamısını birləşdir
        all_streams = popular_live + searched_live
        
        # Təkrarları sil
        unique_streams = []
        seen_ids = set()
        
        for stream in all_streams:
            if stream['video_id'] not in seen_ids:
                unique_streams.append(stream)
                seen_ids.add(stream['video_id'])
        
        print(f"\n🎯 ÜMUMİ TAPILAN CANLI YAYINLAR: {len(unique_streams)}")
        
        # Stream URL-ləri əlavə et
        print("\n🔧 STREAM URL-LƏRİ ALINIR...")
        final_streams = []
        
        for stream in unique_streams:
            stream_url = self.get_stream_url_reliable(stream['video_id'])
            if stream_url:
                stream['stream_url'] = stream_url
                final_streams.append(stream)
                print(f"  ✅ {stream['channel']} - HAZIR")
            else:
                print(f"  ❌ {stream['channel']} - STREAM YOXDUR")
        
        print(f"\n📊 İŞLƏYƏN STREAM-LƏR: {len(final_streams)}/{len(unique_streams)}")
        
        # Əgər az streams varsa, backup əlavə et
        if len(final_streams) < 3:
            print("⚠️ Az stream var, backup əlavə edilir...")
            final_streams.extend(self.get_backup_streams())
        
        # Yadda saxla
        self.save_streams(final_streams)
        return final_streams
    
    def get_backup_streams(self):
        """Backup streamlər"""
        backup_channels = [
            {
                'video_id': 'KpA64R5Jg-4',
                'title': 'SHOW TV Canlı Yayın',
                'channel': 'SHOW TV',
                'is_live': True,
                'url': 'https://www.youtube.com/watch?v=KpA64R5Jg-4',
                'stream_url': self.get_stream_url_reliable('KpA64R5Jg-4'),
                'discovered_at': datetime.now().isoformat()
            },
            {
                'video_id': 'qEQu1Z4Xl_4',
                'title': 'HABERTÜRK TV Canlı Yayın',
                'channel': 'HABERTÜRK TV', 
                'is_live': True,
                'url': 'https://www.youtube.com/watch?v=qEQu1Z4Xl_4',
                'stream_url': self.get_stream_url_reliable('qEQu1Z4Xl_4'),
                'discovered_at': datetime.now().isoformat()
            }
        ]
        
        return [ch for ch in backup_channels if ch['stream_url']]
    
    def save_streams(self, streams):
        """Streamləri fayla yaz"""
        data = {
            'last_update': datetime.now().isoformat(),
            'total_streams': len(streams),
            'streams': streams
        }
        
        with open(f"{self.data_dir}/discovered_channels.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 {len(streams)} canlı yayın qeydə alındı")

def main():
    print("🚀 SUPER YouTube Discover başladı...")
    discover = SuperYouTubeDiscover()
    streams = discover.discover_all_live_streams()
    
    print("\n" + "=" * 70)
    print(f"✅ SİSTEM TAMAMLANDI: {len(streams)} CANLI YAYIN")
    print("✨ By_Kerimoff ✨")
    print("=" * 70)
    
    return streams

if __name__ == "__main__":
    main()
