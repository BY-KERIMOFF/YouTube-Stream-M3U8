#!/usr/bin/env python3
"""
YouTube M3U Generator - No Cookies Version
✨ By_Kerimoff ✨
"""

import json
import os
import re
import time
import requests
from datetime import datetime
from urllib.parse import quote
import subprocess

def renkli_yaz(metin, renk=36):
    print(f"\033[{renk}m{metin}\033[0m")

def get_youtube_live_url_direct(channel_name):
    """YouTube canlı yayın URL - COOKIE OLMADAN"""
    try:
        # Farklı arama terimleri
        search_terms = [
            f"{channel_name} canlı yayın",
            f"{channel_name} live",
            f"{channel_name} yayın akışı"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        for term in search_terms:
            try:
                search_url = f"https://www.youtube.com/results?search_query={quote(term)}&sp=EgJAAQ%3D%3D"  # Canlı yayın filter
                
                response = requests.get(search_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    # Video ID-ləri tap
                    video_ids = re.findall(r'"videoId":"([^"]+)"', response.text)
                    unique_ids = []
                    for vid in video_ids:
                        if vid not in unique_ids and len(vid) == 11:
                            unique_ids.append(vid)
                    
                    # Hər video ID üçün canlı yayın olub yoxla
                    for video_id in unique_ids[:3]:  # İlk 3-ü yoxla
                        is_live, m3u_url = check_video_is_live(video_id)
                        if is_live and m3u_url:
                            return {
                                'video_id': video_id,
                                'title': f"{channel_name} Canlı Yayın",
                                'uploader': channel_name,
                                'm3u_url': m3u_url,
                                'is_live': True
                            }
            except:
                continue
                
    except Exception as e:
        renkli_yaz(f"⚠️ Xəta: {str(e)}", 33)
    
    return None

def check_video_is_live(video_id):
    """Video canlı yayındırmı yoxla - ALTERNATİV METOD"""
    try:
        # YouTube oembed API - cookie tələb etmir
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(oembed_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Oembed başarılı, video var
            # Canlı yayın olub yoxlamaq üçün başqa API
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # HLS URL almaq üçün yt-dlp-ni cookie-siz işlət
            try:
                cmd = [
                    'yt-dlp',
                    '-g',
                    '--format', 'best[protocol^=http]',
                    '--no-warnings',
                    '--extractor-args', 'youtube:player_client=android,web',
                    video_url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                
                if result.returncode == 0 and result.stdout:
                    urls = result.stdout.strip().split('\n')
                    for url in urls:
                        if url.startswith('http') and ('m3u8' in url or 'manifest' in url or 'googlevideo' in url):
                            return True, url
                    # M3U8 yoxdursa ama URL varsa
                    if urls and urls[0].startswith('http'):
                        return True, urls[0]
            except:
                pass
                
    except:
        pass
    
    return False, None

def get_predefined_channel_url(channel_name):
    """Əl ilə təyin edilmiş kanal URL-ləri"""
    # Bəzi kanalların bilinən canlı yayın URL-ləri
    predefined = {
        "TRT Haber": "https://www.youtube.com/watch?v=3fumBcKC6RE",
        "CNN Türk": "https://www.youtube.com/watch?v=2HDAIxJryIA",
        "NTV": "https://www.youtube.com/watch?v=tYQv4n78S2U",
        "Habertürk": "https://www.youtube.com/watch?v=KvFcR0g-R9g",
        "A Haber": "https://www.youtube.com/watch?v=4nQ2c1CJ6YE"
    }
    
    if channel_name in predefined:
        video_url = predefined[channel_name]
        video_id = video_url.split('v=')[1].split('&')[0]
        
        # M3U URL al
        try:
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best',
                '--no-warnings',
                video_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout:
                m3u_url = result.stdout.strip().split('\n')[0]
                if m3u_url.startswith('http'):
                    return {
                        'video_id': video_id,
                        'title': f"{channel_name} Canlı Yayın",
                        'uploader': channel_name,
                        'm3u_url': m3u_url,
                        'is_live': True
                    }
        except:
            pass
    
    return None

def create_m3u_content(channel_name, video_info):
    """M3U fayl məzmunu yarat"""
    content = []
    content.append('#EXTM3U')
    content.append(f'#PLAYLIST:{channel_name}')
    content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    # Logo
    logo_url = f"https://img.youtube.com/vi/{video_info['video_id']}/hqdefault.jpg"
    
    title = f"🔴 {channel_name} CANLI YAYIN"
    content.append(f'#EXTINF:-1 tvg-logo="{logo_url}" tvg-name="{channel_name}",{title}')
    content.append(video_info['m3u_url'])
    
    return '\n'.join(content)

def safe_filename(name):
    """Təhlükəsiz fayl adı"""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

def main():
    print("=" * 80)
    renkli_yaz("🎬 YouTube M3U Generator - Cookie Free", 36)
    renkli_yaz("✨ By_Kerimoff", 33)
    print("=" * 80)
    
    # channels.json oxu
    try:
        with open('channels.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        renkli_yaz("❌ channels.json tapılmadı!", 31)
        # Default channels yarat
        data = {
            "channels": [
                {"name": "TRT Haber", "enabled": True},
                {"name": "CNN Türk", "enabled": True},
                {"name": "NTV", "enabled": True},
                {"name": "Habertürk", "enabled": True},
                {"name": "A Haber", "enabled": True},
                {"name": "Show TV", "enabled": True},
                {"name": "Kanal D", "enabled": True},
                {"name": "NOW TV", "enabled": True}
            ]
        }
    
    channels = [c for c in data['channels'] if c.get('enabled', True)]
    
    renkli_yaz(f"📺 {len(channels)} kanal işlənəcək...", 32)
    
    os.makedirs('m3u_files', exist_ok=True)
    
    results = []
    
    for i, channel in enumerate(channels, 1):
        name = channel['name']
        print(f"\n[{i}/{len(channels)}] 📺 {name}")
        
        video_info = None
        
        # Metod 1: Predefined URL
        renkli_yaz("   🔍 Metod 1: Hazır URL yoxlanılır...", 36)
        video_info = get_predefined_channel_url(name)
        
        # Metod 2: Direct search
        if not video_info:
            renkli_yaz("   🔍 Metod 2: YouTube axtarılır...", 36)
            video_info = get_youtube_live_url_direct(name)
        
        if video_info and video_info.get('m3u_url'):
            m3u_content = create_m3u_content(name, video_info)
            filename = f"m3u_files/{safe_filename(name)}.m3u"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            renkli_yaz(f"   ✅ M3U yaradıldı!", 32)
            renkli_yaz(f"   🔗 URL: {video_info['m3u_url'][:60]}...", 36)
            
            results.append({
                'name': name,
                'status': 'success',
                'file': filename,
                'm3u_url': video_info['m3u_url'],
                'video_id': video_info['video_id']
            })
        else:
            renkli_yaz(f"   ❌ M3U alına bilmədi!", 31)
            results.append({
                'name': name,
                'status': 'failed'
            })
        
        time.sleep(2)
    
    # Ana playlist yarat
    create_master_playlist(results)
    
    # Nəticələr
    print("\n" + "=" * 80)
    renkli_yaz("📊 NƏTİCƏLƏR", 36)
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"✅ Uğurlu: {successful}")
    print(f"❌ Uğursuz: {len(channels) - successful}")
    
    if successful > 0:
        print("\n✅ İŞLƏYƏN KANALLAR:")
        for r in results:
            if r['status'] == 'success':
                print(f"   🎯 {r['name']}")
                print(f"   🔗 Raw URL: https://raw.githubusercontent.com/[USERNAME]/[REPO]/main/{r['file']}")
        
        print("\n📺 BÜTÜN KANALLAR ÜÇÜN PLAYLIST:")
        print("   m3u_files/all_channels.m3u")

def create_master_playlist(results):
    """Bütün kanalların playlisti"""
    content = ['#EXTM3U']
    content.append(f'#PLAYLIST:YouTube Canlı Kanallar')
    content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    content.append('')
    
    for r in results:
        if r['status'] == 'success':
            content.append(f'#EXTINF:-1,🔴 {r["name"]}')
            content.append(r['m3u_url'])
            content.append('')
    
    with open('m3u_files/all_channels.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    renkli_yaz("✅ Master playlist yaradıldı: m3u_files/all_channels.m3u", 32)

if __name__ == "__main__":
    main()
