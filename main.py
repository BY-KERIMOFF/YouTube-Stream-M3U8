#!/usr/bin/env python3
"""
TR YouTube Live Stream Updater
YouTube canlı yayınlarını avtomatik tapır və m3u8 faylları yaradır
"""

import json
import os
import sys
import re
import time
from pathlib import Path
import requests
from urllib.parse import urlparse, parse_qs
import subprocess

# Config
OUTPUT_FOLDER = 'TR'
TIMEOUT = 30
MAX_RETRIES = 2

def get_youtube_live_stream(channel_id, slug, retry=0):
    """YouTube kanalından canlı yayını avtomatik tap"""
    print(f"\n📺 {slug} kanalı yoxlanılır...")
    
    try:
        # 1. YouTube səhifəsini götür
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        # 2. Canlı yayın olub-olmadığını yoxla
        if '"isLive":true' not in response.text and '"liveStreamability"' not in response.text:
            print(f"  ⚠ {slug} canlı yayında deyil")
            return None
        
        print(f"  ✓ {slug} canlı yayında!")
        
        # 3. m3u8 linkini tap (müxtəlif pattern-lər)
        patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'"liveStreamabilityRenderer".*?"streamingUrl":"([^"]+)"',
            r'"streamingUrl":"([^"]+)"',
            r'm3u8.*?(https://[^"\s]+\.m3u8[^"\s]*)',
            r'https://[^"\s]+\.googlevideo\.com[^"\s]*m3u8[^"\s]*',
        ]
        
        m3u8_url = None
        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                m3u8_url = matches[0].replace('\\', '')
                print(f"  ✓ m3u8 tapıldı: {m3u8_url[:80]}...")
                break
        
        if not m3u8_url:
            # 4. yt-dlp ilə cəhd et
            print(f"  ⚠ Avtomatik tapılmadı, yt-dlp cəhd edir...")
            try:
                result = subprocess.run(
                    ['yt-dlp', '-g', '-f', 'best', f'https://www.youtube.com/channel/{channel_id}/live'],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                if result.stdout:
                    m3u8_url = result.stdout.strip()
                    print(f"  ✓ yt-dlp ilə tapıldı: {m3u8_url[:80]}...")
            except:
                pass
        
        if m3u8_url:
            # 5. m3u8 məzmununu götür
            m3u8_response = requests.get(m3u8_url, headers=headers, timeout=TIMEOUT)
            if '#EXTM3U' in m3u8_response.text:
                print(f"  ✓ m3u8 yükləndi ({len(m3u8_response.text)} bayt)")
                return m3u8_response.text
        
        return None
        
    except Exception as e:
        print(f"  ✗ Xəta: {type(e).__name__}")
        if retry < MAX_RETRIES:
            print(f"  → Yenidən cəhd... ({retry+1}/{MAX_RETRIES})")
            time.sleep(2)
            return get_youtube_live_stream(channel_id, slug, retry + 1)
        return None

def get_video_stream(video_id, slug, retry=0):
    """YouTube video ID-dən stream götür"""
    print(f"\n🎬 {slug} videosu yoxlanılır...")
    
    try:
        # yt-dlp ilə video stream-i götür
        try:
            result = subprocess.run(
                ['yt-dlp', '-g', '-f', 'best', f'https://www.youtube.com/watch?v={video_id}'],
                capture_output=True,
                text=True,
                timeout=20
            )
            if result.stdout:
                stream_url = result.stdout.strip()
                print(f"  ✓ Stream tapıldı: {stream_url[:80]}...")
                
                # m3u8 formatına çevir
                m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
{stream_url}
"""
                return m3u8_content
        except Exception as e:
            print(f"  ⚠ yt-dlp xətası: {e}")
        
        return None
        
    except Exception as e:
        print(f"  ✗ Xəta: {type(e).__name__}")
        if retry < MAX_RETRIES:
            time.sleep(2)
            return get_video_stream(video_id, slug, retry + 1)
        return None

def create_m3u8_file(stream_config, m3u8_content):
    """m3u8 faylı yarat"""
    slug = stream_config['slug']
    subfolder = stream_config.get('subfolder', 'genel')
    
    # TR qovluğunu və alt qovluğu yarat
    output_dir = Path(OUTPUT_FOLDER) / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{slug}.m3u8"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(m3u8_content)
        print(f"  💾 Saxlandı: {output_file}")
        return True
    except Exception as e:
        print(f"  ✗ Saxlana bilmədi: {e}")
        return False

def check_ytdlp():
    """yt-dlp yüklüdür mü?"""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        print("✓ yt-dlp yüklüdür")
        return True
    except:
        print("⚠ yt-dlp yüklü deyil, yüklənir...")
        try:
            subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            print("✓ yt-dlp yükləndi")
            return True
        except Exception as e:
            print(f"✗ yt-dlp yüklənə bilmədi: {e}")
            return False

def process_streams(config_file):
    """Bütün stream-ləri işlə"""
    print(f"\n📁 Config faylı oxunur: {config_file}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            streams = json.load(f)
    except Exception as e:
        print(f"✗ Config oxuna bilmədi: {e}")
        return 0, 0
    
    print(f"✓ {len(streams)} stream tapıldı")
    
    # yt-dlp yoxla
    ytdlp_available = check_ytdlp()
    
    successful = 0
    failed = 0
    
    # TR qovluğunu yarat
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    for i, stream in enumerate(streams, 1):
        stream_type = stream.get('type', 'channel')
        stream_id = stream['id']
        slug = stream['slug']
        name = stream['name']
        
        print(f"\n[{i}/{len(streams)}] 🔄 {name} ({slug})")
        print("-" * 40)
        
        m3u8_content = None
        
        if stream_type == 'channel':
            m3u8_content = get_youtube_live_stream(stream_id, slug)
        elif stream_type == 'video':
            m3u8_content = get_video_stream(stream_id, slug)
        
        if m3u8_content:
            if create_m3u8_file(stream, m3u8_content):
                successful += 1
            else:
                failed += 1
        else:
            print(f"  ✗ Stream tapılmadı")
            failed += 1
    
    return successful, failed

def main():
    """Əsas funksiya"""
    print("=" * 60)
    print("🎯 TR YouTube Canlı Yayın Toplayıcı")
    print("=" * 60)
    print("📺 YouTube canlı yayınları avtomatik tapılır")
    print("💾 TR qovluğunda m3u8 faylları yaradılır")
    print("=" * 60)
    
    # Lazımlı paketləri yüklə
    print("\n📦 Lazımlı paketlər yoxlanılır...")
    try:
        import requests
        print("✓ requests yüklüdür")
    except:
        print("⚠ requests yoxdur, yüklənir...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)
    
    # Config faylını yoxla
    config_file = 'turkish.json'
    if not Path(config_file).exists():
        print(f"\n✗ {config_file} tapılmadı!")
        print(f"ℹ Nümunə config yaradılır...")
        create_sample_config()
        config_file = 'turkish.json'
    
    # Stream-ləri işlə
    successful, failed = process_streams(config_file)
    
    # Nəticə
    print("\n" + "=" * 60)
    print("📊 NƏTİCƏ")
    print("=" * 60)
    print(f"✅ Uğurlu: {successful}")
    print(f"❌ Uğursuz: {failed}")
    print(f"📁 Çıxış qovluğu: {OUTPUT_FOLDER}/")
    
    # TR qovluğunun məzmununu göstər
    print(f"\n📂 {OUTPUT_FOLDER} qovluğunun məzmunu:")
    try:
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            level = root.replace(OUTPUT_FOLDER, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📁 {os.path.basename(root) or OUTPUT_FOLDER}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.m3u8'):
                    print(f"{subindent}📄 {file}")
    except:
        pass
    
    print("=" * 60)
    
    if successful > 0:
        print("🎉 Uğurlu! TR qovluğunda m3u8 faylları yaradıldı.")
    else:
        print("⚠ Heç bir stream tapılmadı!")

def create_sample_config():
    """Nümunə config faylı yarat"""
    sample_config = [
        {
            "type": "channel",
            "name": "24 TV",
            "slug": "24tv",
            "id": "UCN7VYCsI4Lx1-J4_BtjoWUA",
            "subfolder": "haber"
        },
        {
            "type": "channel",
            "name": "TRT Haber",
            "slug": "trthaber",
            "id": "UCBgTP2LOFVPmq15W-RH-WXA",
            "subfolder": "haber"
        },
        {
            "type": "channel", 
            "name": "A Spor",
            "slug": "aspor",
            "id": "UCJElRTCNEmLemgirqvsW63Q",
            "subfolder": "spor"
        },
        {
            "type": "video",
            "name": "Örnek Video",
            "slug": "ornek-video",
            "id": "dQw4w9WgXcQ",
            "subfolder": "diger"
        }
    ]
    
    with open('turkish.json', 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print("✓ Nümunə turkish.json yaradıldı")

if __name__ == "__main__":
    main()
