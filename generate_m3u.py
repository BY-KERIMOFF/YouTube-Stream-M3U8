#!/usr/bin/env python3
"""
YouTube M3U Generator - Improved Version
✨ By_Kerimoff ✨
"""

import subprocess
import json
import os
import sys
import time
import re
import requests
from datetime import datetime
from urllib.parse import quote

def renkli_yaz(metin, renk=36):
    print(f"\033[{renk}m{metin}\033[0m")

def get_youtube_live_url(channel_name):
    """YouTube canlı yayın URL-ni tap - ALTERNATİV METOD"""
    try:
        # Metod 1: YouTube search API
        search_url = f"https://www.youtube.com/results?search_query={quote(channel_name + ' canlı yayın')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Canlı yayın video ID-lərini tap
            # Pattern: "videoId":"XXXXXXXXXXX" ve "badges" içinde "LIVE" olanlar
            video_ids = re.findall(r'"videoId":"([^"]+)"', response.text)
            
            # Canlı yayınları filtrele
            for video_id in video_ids:
                if len(video_id) == 11:
                    # Video bilgisini al
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    try:
                        cmd = [
                            'yt-dlp',
                            '--dump-json',
                            '--no-warnings',
                            '--skip-download',
                            '--socket-timeout', '10',
                            video_url
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                        
                        if result.returncode == 0:
                            info = json.loads(result.stdout)
                            if info.get('is_live'):
                                # M3U URL al
                                m3u_url = get_m3u_from_video(video_url)
                                if m3u_url:
                                    return {
                                        'video_id': video_id,
                                        'title': info.get('title', ''),
                                        'uploader': info.get('uploader', ''),
                                        'm3u_url': m3u_url,
                                        'is_live': True
                                    }
                    except:
                        continue
        return None
        
    except Exception as e:
        renkli_yaz(f"⚠️ Xəta: {str(e)}", 33)
        return None

def get_m3u_from_video(video_url):
    """Video URL-dən M3U linkini al"""
    try:
        # yt-dlp ilə M3U URL al
        cmd = [
            'yt-dlp',
            '-g',
            '--format', 'best',
            '--no-warnings',
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            urls = result.stdout.strip().split('\n')
            for url in urls:
                if url.startswith('http') and ('m3u8' in url or 'manifest' in url):
                    return url
            # M3U8 yoxdursa ilk URL-i qaytar
            if urls and urls[0].startswith('http'):
                return urls[0]
    except:
        pass
    return None

def search_with_ytdlp(channel_name):
    """yt-dlp ilə axtar (Alternativ)"""
    try:
        cmd = [
            'yt-dlp',
            f'ytsearch1:"{channel_name} canlı yayın"',
            '--dump-json',
            '--no-warnings',
            '--skip-download',
            '--socket-timeout', '15'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line:
                    try:
                        info = json.loads(line)
                        if info.get('is_live'):
                            video_url = f"https://www.youtube.com/watch?v={info['id']}"
                            m3u_url = get_m3u_from_video(video_url)
                            if m3u_url:
                                return {
                                    'video_id': info['id'],
                                    'title': info.get('title', ''),
                                    'uploader': info.get('uploader', ''),
                                    'm3u_url': m3u_url,
                                    'is_live': True
                                }
                    except:
                        continue
    except:
        pass
    return None

def get_channel_m3u(channel_name):
    """Kanal üçün M3U URL al - BÜTÜN METODLAR"""
    
    # Metod 1: yt-dlp ilə
    renkli_yaz("   🔍 Metod 1: yt-dlp ilə axtarılır...", 36)
    result = search_with_ytdlp(channel_name)
    if result:
        return result
    
    # Metod 2: Direct search
    renkli_yaz("   🔍 Metod 2: Direct axtarılır...", 36)
    result = get_youtube_live_url(channel_name)
    if result:
        return result
    
    # Metod 3: Farklı arama terimleri
    search_terms = [
        f"{channel_name} canlı",
        f"{channel_name} live",
        f"{channel_name} yayın",
        f"{channel_name} canlı yayın"
    ]
    
    for term in search_terms:
        renkli_yaz(f"   🔍 Metod 3: '{term}' axtarılır...", 36)
        try:
            cmd = [
                'yt-dlp',
                f'ytsearch1:"{term}"',
                '--dump-json',
                '--no-warnings',
                '--skip-download'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and result.stdout:
                info = json.loads(result.stdout.strip().split('\n')[0])
                video_url = f"https://www.youtube.com/watch?v={info['id']}"
                m3u_url = get_m3u_from_video(video_url)
                if m3u_url:
                    return {
                        'video_id': info['id'],
                        'title': info.get('title', ''),
                        'uploader': info.get('uploader', ''),
                        'm3u_url': m3u_url,
                        'is_live': info.get('is_live', False)
                    }
        except:
            continue
    
    return None

def create_m3u_content(channel_name, video_info):
    """M3U fayl məzmunu yarat"""
    content = []
    content.append('#EXTM3U')
    content.append(f'#PLAYLIST:{channel_name}')
    content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    content.append(f'#NAME:{channel_name}')
    
    # Logo
    logo_url = f"https://img.youtube.com/vi/{video_info['video_id']}/maxresdefault.jpg"
    
    # Kanal məlumatı
    status = "🔴 LIVE" if video_info.get('is_live') else "📹 VIDEO"
    title = f"{status} | {channel_name} | {video_info['title'][:100]}"
    
    content.append(f'#EXTINF:-1 tvg-logo="{logo_url}" tvg-name="{channel_name}",{title}')
    content.append(video_info['m3u_url'])
    
    return '\n'.join(content)

def safe_filename(name):
    """Təhlükəsiz fayl adı"""
    name = name.lower()
    name = re.sub(r'[^a-z0-9ğüşıöç]', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

def update_channels_json_with_urls(channels_data, results):
    """JSON faylını M3U URL-ləri ilə yenilə"""
    for result in results:
        if result['status'] == 'success':
            for channel in channels_data['channels']:
                if channel['name'] == result['name']:
                    channel['m3u_url'] = result['m3u_url']
                    channel['video_id'] = result['video_id']
                    channel['last_update'] = datetime.now().isoformat()
                    channel['title'] = result['title']
    
    channels_data['last_update'] = datetime.now().isoformat()
    channels_data['total_success'] = len([r for r in results if r['status'] == 'success'])
    channels_data['total_failed'] = len([r for r in results if r['status'] == 'failed'])
    
    with open('channels.json', 'w', encoding='utf-8') as f:
        json.dump(channels_data, f, indent=2, ensure_ascii=False)
    
    renkli_yaz("✅ channels.json yeniləndi!", 32)

def create_m3u_playlist(results):
    """Bütün kanalları birləşdirən əsas M3U playlist yarat"""
    content = []
    content.append('#EXTM3U')
    content.append(f'#PLAYLIST:YouTube Canlı Kanallar')
    content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    content.append('')
    
    for result in results:
        if result['status'] == 'success':
            status = "🔴 LIVE" if result.get('is_live') else "📹 VIDEO"
            title = f"{status} | {result['name']}"
            content.append(f'#EXTINF:-1,{title}')
            content.append(result['m3u_url'])
            content.append('')
    
    # Əsas playlist-i saxla
    with open('m3u_files/all_channels.m3u', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    renkli_yaz("✅ all_channels.m3u yaradıldı!", 32)

def main():
    print("=" * 80)
    renkli_yaz("🎬 YouTube M3U Generator - By_Kerimoff", 36)
    print("=" * 80)
    
    # yt-dlp yoxla
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        renkli_yaz("✅ yt-dlp hazırdır!", 32)
    except:
        renkli_yaz("❌ yt-dlp yoxdur! Quraşdırın: pip install yt-dlp", 31)
        sys.exit(1)
    
    # channels.json oxu
    try:
        with open('channels.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        renkli_yaz("❌ channels.json tapılmadı!", 31)
        sys.exit(1)
    except Exception as e:
        renkli_yaz(f"❌ JSON oxuma xətası: {str(e)}", 31)
        sys.exit(1)
    
    channels = data.get('channels', [])
    enabled_channels = [c for c in channels if c.get('enabled', True)]
    
    renkli_yaz(f"📺 {len(enabled_channels)} kanal işlənəcək...", 32)
    
    # m3u_files qovluğu yarat
    os.makedirs('m3u_files', exist_ok=True)
    
    results = []
    
    for i, channel in enumerate(enabled_channels, 1):
        name = channel['name']
        print(f"\n[{i}/{len(enabled_channels)}] 📺 {name}")
        
        # M3U URL al
        video_info = get_channel_m3u(name)
        
        if video_info and video_info.get('m3u_url'):
            # M3U faylını yarat
            m3u_content = create_m3u_content(name, video_info)
            filename = f"m3u_files/{safe_filename(name)}.m3u"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            renkli_yaz(f"   ✅ M3U yaradıldı!", 32)
            renkli_yaz(f"   📹 Video: {video_info['title'][:70]}...", 36)
            renkli_yaz(f"   🔗 URL: {video_info['m3u_url'][:70]}...", 36)
            
            results.append({
                'name': name,
                'status': 'success',
                'file': filename,
                'video_id': video_info['video_id'],
                'title': video_info['title'],
                'm3u_url': video_info['m3u_url'],
                'is_live': video_info.get('is_live', False)
            })
        else:
            renkli_yaz(f"   ❌ M3U alına bilmədi!", 31)
            results.append({
                'name': name,
                'status': 'failed'
            })
        
        # Rate limit üçün gözlə
        time.sleep(3)
    
    # JSON faylını yenilə
    update_channels_json_with_urls(data, results)
    
    # Bütün kanalların playlistini yarat
    create_m3u_playlist(results)
    
    # Nəticələri göstər
    print("\n" + "=" * 80)
    renkli_yaz("📊 NƏTİCƏLƏR", 36)
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len([r for r in results if r['status'] == 'failed'])
    print(f"✅ Uğurlu: {successful}")
    print(f"❌ Uğursuz: {failed}")
    print(f"📁 M3U faylları: m3u_files/ qovluğunda")
    
    if successful > 0:
        print("\n🎯 İŞLƏYƏN KANALLAR:")
        for r in results:
            if r['status'] == 'success':
                print(f"   ✅ {r['name']}")
        
        print("\n🔗 BÜTÜN KANALLAR ÜÇÜN PLAYLIST:")
        print(f"   https://raw.githubusercontent.com/[USERNAME]/[REPO]/main/m3u_files/all_channels.m3u")
    
    renkli_yaz("\n✅ İŞLEM TAMAMLANDI!", 32)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        renkli_yaz("👋 Dayandırıldı!", 35)
    except Exception as e:
        renkli_yaz(f"\n❌ Xəta: {str(e)}", 31)
