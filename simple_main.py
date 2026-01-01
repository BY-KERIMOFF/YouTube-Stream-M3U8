#!/usr/bin/env python3
"""
YouTube-dan birbaşa m3u8 çıxaran sadə skript
API ehtiyacı YOXDUR!
"""

import json
import os
import sys
import re
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def get_youtube_stream(channel_id):
    """
    YouTube-dan birbaşa m3u8 linki al
    """
    try:
        # YouTube kanal URL-i
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"  → YouTube-a giriş: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  ✗ YouTube səhifəsi yoxdur: {response.status_code}")
            return None
        
        # HTML-dən m3u8 linki axtar
        html = response.text
        
        # 1. YouTube-nun daxili m3u8 linkini tap
        patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'"url":"([^"{}]+m3u8[^"{}]*)"',
            r'https[^"\s]+m3u8[^"\s]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if 'm3u8' in match:
                    # URL-ni təmizlə
                    m3u8_url = match.replace('\\/', '/')
                    print(f"  ✓ m3u8 tapıldı: {m3u8_url[:80]}...")
                    return m3u8_url
        
        print("  ✗ m3u8 linki tapılmadı")
        return None
        
    except Exception as e:
        print(f"  ✗ Xəta: {e}")
        return None

def save_m3u8_file(slug, m3u8_url, output_folder="TR"):
    """
    m3u8 faylını yadda saxla
    """
    try:
        # m3u8 məzmununu yüklə
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.youtube.com/'
        }
        
        response = requests.get(m3u8_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  ✗ m3u8 yüklənmədi: {response.status_code}")
            return False
        
        m3u8_content = response.text
        
        # Faylı yaz
        output_dir = Path(output_folder)
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{slug}.m3u8"
        
        with open(output_file, 'w') as f:
            f.write(m3u8_content)
        
        print(f"  ✓ Fayl yaradıldı: {output_file}")
        return True
        
    except Exception as e:
        print(f"  ✗ Fayl yazıla bilmədi: {e}")
        return False

def main():
    # Config faylını yüklə
    config_file = "turkish.json"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except:
        print(f"✗ {config_file} tapılmadı")
        return
    
    print(f"📊 {len(config)} kanal tapıldı")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for channel in config:
        slug = channel.get('slug', 'unknown')
        channel_id = channel.get('id', '')
        
        print(f"\n🔴 {slug}")
        print(f"   ID: {channel_id}")
        
        if not channel_id:
            print("  ✗ ID yoxdur")
            failed += 1
            continue
        
        # YouTube-dan m3u8 al
        m3u8_url = get_youtube_stream(channel_id)
        
        if m3u8_url:
            # Faylı yadda saxla
            if save_m3u8_file(slug, m3u8_url):
                successful += 1
            else:
                failed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Uğurlu: {successful}")
    print(f"❌ Uğursuz: {failed}")
    print("=" * 50)

if __name__ == "__main__":
    main()
