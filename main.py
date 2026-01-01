#!/usr/bin/env python3
"""
TR YouTube Live Stream Updater
YouTube canlı yayınlarını avtomatik tapır və TR qovluğuna m3u8 yaradır
"""

import json
import os
import sys
import re
import time
from pathlib import Path
import requests
import subprocess

# Config
OUTPUT_FOLDER = 'TR'

def get_youtube_stream(channel_id, slug):
    """YouTube kanalından canlı yayını tap"""
    try:
        print(f"🔍 {slug} kanalı yoxlanılır...")
        
        # YouTube səhifəsini götür
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # Canlı yayın yoxla
        if '"isLive":true' not in response.text:
            print(f"  ⚠ {slug} canlı yayında deyil")
            return None
        
        print(f"  ✅ {slug} canlı yayında!")
        
        # yt-dlp ilə stream tap
        try:
            result = subprocess.run(
                ['yt-dlp', '-g', '-f', 'best', url],
                capture_output=True,
                text=True,
                timeout=20
            )
            if result.stdout:
                stream_url = result.stdout.strip()
                print(f"  ✅ Stream tapıldı")
                
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
        print(f"  ❌ Xəta: {e}")
        return None

def save_m3u8(stream_info, content):
    """m3u8 faylını saxla"""
    slug = stream_info['slug']
    subfolder = stream_info.get('subfolder', 'genel')
    
    # Qovluğu yarat
    output_dir = Path(OUTPUT_FOLDER) / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{slug}.m3u8"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 Saxlandı: {output_file}")
        return True
    except Exception as e:
        print(f"  ❌ Saxlana bilmədi: {e}")
        return False

def main():
    """Əsas proqram"""
    print("=" * 50)
    print("🎬 TR YouTube Stream Updater")
    print("=" * 50)
    
    # Config faylını yoxla
    config_file = 'turkish.json'
    if not os.path.exists(config_file):
        print(f"❌ {config_file} tapılmadı!")
        return
    
    # Config oxu
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            streams = json.load(f)
        print(f"✅ {len(streams)} stream tapıldı")
    except Exception as e:
        print(f"❌ Config oxuna bilmədi: {e}")
        return
    
    # TR qovluğunu yarat
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    successful = 0
    total = len(streams)
    
    # Hər stream-i işlə
    for i, stream in enumerate(streams, 1):
        print(f"\n[{i}/{total}] {stream['name']}")
        print("-" * 30)
        
        if stream.get('type') == 'video':
            print(f"  ⚡ Video stream - keçilir")
            continue
        
        content = get_youtube_stream(stream['id'], stream['slug'])
        
        if content:
            if save_m3u8(stream, content):
                successful += 1
        else:
            print(f"  ❌ Stream tapılmadı")
    
    # Nəticə
    print("\n" + "=" * 50)
    print(f"📊 Nəticə: {successful}/{total} uğurlu")
    print(f"📁 Çıxış: {OUTPUT_FOLDER}/")
    
    # Faylları göstər
    print("\n📂 Yaradılan fayllar:")
    for root, dirs, files in os.walk(OUTPUT_FOLDER):
        for file in files:
            if file.endswith('.m3u8'):
                print(f"  📄 {os.path.join(root, file)}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
