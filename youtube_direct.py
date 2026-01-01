#!/usr/bin/env python3
"""
YouTube-dan birbaşa m3u8 çıxaran skript
turkish.json-dakı bütün kanalları avtomatik yükləyir
"""

import json
import re
import requests
import time
import sys
from pathlib import Path

def get_youtube_stream(channel_id, is_video=False):
    """
    YouTube-dan m3u8 linki al
    """
    try:
        if is_video:
            url = f"https://www.youtube.com/watch?v={channel_id}"
        else:
            url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        print(f"  → YouTube: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"  ✗ Xəta: {response.status_code}")
            return None
        
        html = response.text
        
        # m3u8 linkini tap
        patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'"url":"([^"{}]+m3u8[^"{}]*)"',
            r'https[^"\s]+m3u8[^"\s]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if 'm3u8' in match:
                    # URL-i təmizlə
                    m3u8_url = match.replace('\\/', '/')
                    print(f"  ✓ m3u8 tapıldı")
                    return m3u8_url
        
        print("  ✗ m3u8 tapılmadı")
        return None
        
    except Exception as e:
        print(f"  ✗ Xəta: {e}")
        return None

def save_m3u8(slug, m3u8_url, subfolder=""):
    """
    m3u8 faylını yadda saxla
    """
    try:
        # m3u8 məzmununu yüklə
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.youtube.com/'
        }
        
        response = requests.get(m3u8_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  ✗ m3u8 yüklənmədi: {response.status_code}")
            return False
        
        m3u8_content = response.text
        
        # Qovluq yarat
        if subfolder:
            output_dir = Path("TR") / subfolder
        else:
            output_dir = Path("TR")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fayl adı
        output_file = output_dir / f"{slug}.m3u8"
        
        # Faylı yaz
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(m3u8_content)
        
        print(f"  ✓ Fayl: {output_file}")
        return True
        
    except Exception as e:
        print(f"  ✗ Fayl yazıla bilmədi: {e}")
        return False

def main():
    print("=" * 60)
    print("YouTube M3U8 Yükləyici")
    print("=" * 60)
    
    # turkish.json yüklə
    try:
        with open('turkish.json', 'r', encoding='utf-8') as f:
            channels = json.load(f)
        print(f"📊 {len(channels)} kanal tapıldı")
    except Exception as e:
        print(f"✗ turkish.json yüklənə bilmədi: {e}")
        return
    
    successful = 0
    failed = 0
    
    # Hər kanal üçün
    for i, channel in enumerate(channels, 1):
        name = channel.get('name', 'Naməlum')
        slug = channel.get('slug', 'unknown')
        channel_id = channel.get('id', '')
        channel_type = channel.get('type', 'channel')
        subfolder = channel.get('subfolder', '')
        
        print(f"\n[{i}/{len(channels)}] {name} ({slug})")
        
        if not channel_id:
            print("  ✗ ID yoxdur")
            failed += 1
            continue
        
        # YouTube-dan m3u8 al
        is_video = (channel_type == 'video')
        m3u8_url = get_youtube_stream(channel_id, is_video)
        
        if m3u8_url:
            # Faylı yadda saxla
            if save_m3u8(slug, m3u8_url, subfolder):
                successful += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # Qısa fasilə ver (YouTube ban etməsin)
        time.sleep(1)
    
    # Nəticə
    print("\n" + "=" * 60)
    print(f"✅ UĞURLU: {successful}")
    print(f"❌ UĞURSUZ: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
