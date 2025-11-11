#!/usr/bin/env python3
"""
YouTube-dan avtomatik canlı yayın kəşfiyyatçısı - FIXED
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
            "canlı", "live", "stream", 
            "türk", "turkey", "tv",
            "spor", "haber", "müzik"
        ]
        return trends
    
    def search_youtube_live(self, query):
        """YouTube-da canlı yayın axtarır - YENİ ÜSUL"""
        try:
            print(f"🎯 Axtarılır: '{query}'")
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}&sp=EgJAAQ%253D%253D"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            response = requests.get(search_url, headers=headers, timeout=25)
            response.raise_for_status()
            
            # YouTube JSON məlumatını tap
            json_data = self.extract_yt_initial_data(response.text)
            if not json_data:
                print(f"❌ JSON data tapılmadı: {query}")
                return []
            
            # Video ID-ləri çıxar
            video_ids = self.extract_video_ids_from_json(json_data)
            print(f"📹 Tapılan video ID-ləri: {len(video_ids)}")
            
            live_streams = []
            for video_id in video_ids[:8]:  # İlk 8
                print(f"  🔍 Yoxlanılır: {video_id}")
                stream_info = self.get_stream_info_simple(video_id)
                if stream_info:
                    live_streams.append(stream_info)
                    print(f"  ✅ TAPILDI: {stream_info['title'][:50]}...")
                else:
                    print(f"  ❌ Məlumat alınmadı: {video_id}")
                
                time.sleep(1)
                
            print(f"🎉 '{query}' üçün {len(live_streams)} canlı yayın tapıldı")
            return live_streams
            
        except Exception as e:
            print(f"❌ Axtarış xətası '{query}': {str(e)}")
            return []
    
    def extract_yt_initial_data(self, html_content):
        """YouTube səhifəsindən initial data çıxarır"""
        try:
            # var ytInitialData pattern
            pattern = r'var ytInitialData\s*=\s*({.*?});'
            match = re.search(pattern, html_content)
            if match:
                return json.loads(match.group(1))
            
            # window["ytInitialData"] pattern
            pattern2 = r'window\["ytInitialData"\]\s*=\s*({.*?});'
            match2 = re.search(pattern2, html_content)
            if match2:
                return json.loads(match2.group(1))
                
        except Exception as e:
            print(f"❌ JSON extract xətası: {e}")
        
        return None
    
    def extract_video_ids_from_json(self, json_data):
        """JSON datadan video ID-ləri çıxarır"""
        video_ids = []
        
        try:
            # YouTube strukturunda video ID-ləri tap
            contents = json_data.get('contents', {})
            twoColumnSearchResults = contents.get('twoColumnSearchResultsRenderer', {})
            primaryContents = twoColumnSearchResults.get('primaryContents', {})
            sectionListRenderer = primaryContents.get('sectionListRenderer', {})
            contents_list = sectionListRenderer.get('contents', [])
            
            for content in contents_list:
                itemSectionRenderer = content.get('itemSectionRenderer', {})
                items = itemSectionRenderer.get('contents', [])
                
                for item in items:
                    videoRenderer = item.get('videoRenderer', {})
                    if videoRenderer and videoRenderer.get('videoId'):
                        video_id = videoRenderer['videoId']
                        # Yalnız canlı yayınları yoxla
                        if videoRenderer.get('badges'):
                            for badge in videoRenderer['badges']:
                                badge_renderer = badge.get('metadataBadgeRenderer', {})
                                if 'LIVE' in badge_renderer.get('label', '').upper():
                                    video_ids.append(video_id)
                                    break
            
            # Əgər canlı tapılmadısa, bütün videoları götür
            if not video_ids:
                for content in contents_list:
                    itemSectionRenderer = content.get('itemSectionRenderer', {})
                    items = itemSectionRenderer.get('contents', [])
                    
                    for item in items:
                        videoRenderer = item.get('videoRenderer', {})
                        if videoRenderer and videoRenderer.get('videoId'):
                            video_ids.append(videoRenderer['videoId'])
            
        except Exception as e:
            print(f"❌ Video ID extract xətası: {e}")
            
            # Alternativ: regex ilə tap
            html_str = json.dumps(json_data)
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html_str)
            video_ids = list(set(video_ids))  # Təkrarları sil
        
        return video_ids
    
    def get_stream_info_simple(self, video_id):
        """Sadə üsulla video məlumatlarını alır"""
        try:
            # yt-dlp ilə sadə məlumat
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '--print', '%(title)s:::%(uploader)s:::%(is_live)s',
                '--no-warnings',
                '--socket-timeout', '20',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(':::')
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
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'discovered_at': datetime.now().isoformat()
                        }
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Timeout: {video_id}")
        except Exception as e:
            print(f"  ❌ Sadə məlumat xətası {video_id}: {str(e)}")
        
        return None
    
    def get_stream_url(self, video_id):
        """Canlı yayın URL-ni alır - YENİ FORMAT"""
        try:
            print(f"  🌐 Stream URL alınır: {video_id}")
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Əvvəlcə ən yaxşı formatı sınayırıq
            formats = [
                'best[height<=720]',
                'best[height<=480]', 
                'best',
                'worst'
            ]
            
            for format_str in formats:
                try:
                    cmd = [
                        'yt-dlp',
                        '-g',
                        '--format', format_str,
                        '--no-warnings',
                        '--socket-timeout', '15',
                        url
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                    
                    if result.returncode == 0:
                        stream_url = result.stdout.strip()
                        if stream_url and stream_url.startswith('http'):
                            print(f"  ✅ Stream URL alındı ({format_str}): {video_id}")
                            return stream_url
                            
                except:
                    continue
                    
            print(f"  ❌ Heç bir format işləmədi: {video_id}")
                    
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
            
            # 2 saniyə gözlə
            if i < len(keywords):
                print("⏳ 2 saniyə gözlənir...")
                time.sleep(2)
        
        # Təkrar elementləri sil
        unique_streams = []
        seen_ids = set()
        
        for stream in all_live_streams:
            if stream['video_id'] not in seen_ids:
                unique_streams.append(stream)
                seen_ids.add(stream['video_id'])
        
        print(f"\n🎯 ÜMUMİ TAPILAN CANLI YAYINLAR: {len(unique_streams)}")
        
        # Əgər canlı tapılmadısa, məşhur kanalları əlavə et
        if len(unique_streams) == 0:
            print("⚠️ Heç canlı tapılmadı, məşhur kanallar əlavə edilir...")
            unique_streams = self.get_popular_channels()
        
        # Fayla yaz
        self.save_discovered_streams(unique_streams)
        return unique_streams
    
    def get_popular_channels(self):
        """Məşhur YouTube kanallarının listi"""
        popular_channels = [
            {
                'video_id': 'KpA64R5Jg-4',
                'title': 'SHOW TV Canlı Yayın',
                'channel': 'SHOW TV',
                'is_live': True,
                'view_count': 0,
                'url': 'https://www.youtube.com/watch?v=KpA64R5Jg-4',
                'discovered_at': datetime.now().isoformat()
            },
            {
                'video_id': 'qEQu1Z4Xl_4', 
                'title': 'HABERTÜRK TV Canlı Yayın',
                'channel': 'HABERTÜRK TV',
                'is_live': True,
                'view_count': 0,
                'url': 'https://www.youtube.com/watch?v=qEQu1Z4Xl_4',
                'discovered_at': datetime.now().isoformat()
            },
            {
                'video_id': '0TQZLK4kKcI',
                'title': 'CNN TÜRK Canlı Yayın', 
                'channel': 'CNN TÜRK',
                'is_live': True,
                'view_count': 0,
                'url': 'https://www.youtube.com/watch?v=0TQZLK4kKcI',
                'discovered_at': datetime.now().isoformat()
            }
        ]
        return popular_channels
    
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
    print("\n🔧 STREAM URL-LƏRİ YOXLANILIR...")
    working_streams = 0
    for stream in streams:
        stream_url = discover.get_stream_url(stream['video_id'])
        if stream_url:
            working_streams += 1
            print(f"  ✅ {stream['channel']} - İŞLƏYİR")
        else:
            print(f"  ❌ {stream['channel']} - İŞLƏMİR")
    
    print(f"\n📊 İŞLƏYƏN STREAM-LƏR: {working_streams}/{len(streams)}")
    
    return streams

if __name__ == "__main__":
    main()
