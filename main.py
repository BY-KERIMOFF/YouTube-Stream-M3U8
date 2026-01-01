#!/usr/bin/env python3
"""
TR YouTube Stream Updater
YouTube stream URL-lərini gətirir və TR qovluğunda m3u8 faylları yaradır
"""

import json
import os
import sys
import argparse
import time
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs

import cloudscraper
import requests

# Config
ENDPOINT = os.environ.get('ENDPOINT', 'https://your-endpoint.com')
FOLDER_NAME = 'TR'
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2

def create_session():
    """HTTP session yarat"""
    print("✓ Cloudscraper istifadə olunur")
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        },
        delay=10
    )
    return scraper

session = create_session()

def load_config(config_path):
    """JSON config faylını yüklə"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✓ {len(config)} stream yükləndi")
        return config
    except Exception as e:
        print(f"✗ Config faylı oxuna bilmədi: {e}")
        sys.exit(1)

def fetch_stream_url(stream_config, attempt=1):
    """YouTube stream m3u8 URL-ni gətir"""
    stream_type = stream_config.get('type', 'channel')
    stream_id = stream_config['id']
    slug = stream_config['slug']
    
    # URL qur
    query_param = 'v' if stream_type == 'video' else 'c'
    url = f"{ENDPOINT}/yt.php?{query_param}={stream_id}"
    
    print(f"  Gətirilir: {slug}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = session.get(url, timeout=TIMEOUT, headers=headers)
        
        print(f"  → Status: {response.status_code}")
        print(f"  → Ölçü: {len(response.content)} bayt")
        
        response.raise_for_status()
        
        # m3u8 yoxla
        content_preview = response.text[:200]
        
        if '#EXTM3U' in content_preview:
            print(f"  ✓ m3u8 tapıldı")
            return response.text, None
        else:
            print(f"  ✗ m3u8 tapılmadı")
            return None, 'NoM3U8'
        
    except Exception as e:
        print(f"  ✗ Xəta: {type(e).__name__}")
        return None, type(e).__name__

def fetch_with_retry(stream_config):
    """Yenidən cəhd etmə ilə stream gətir"""
    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            delay = RETRY_DELAY * (2 ** (attempt - 2))
            print(f"  → {attempt}/{MAX_RETRIES} yenidən cəhd {delay}s sonra...")
            time.sleep(delay)
        
        result, error = fetch_stream_url(stream_config, attempt)
        if result is not None:
            return result, None
        
        print(f"  → Cəhd {attempt} uğursuz oldu")
    
    print(f"  ✗ Bütün {MAX_RETRIES} cəhd uğursuz oldu")
    return None, 'AllFailed'

def get_output_path(stream_config):
    """Çıxış faylının yolunu al"""
    slug = stream_config['slug']
    subfolder = stream_config.get('subfolder', '')
    
    # TR içində subfolder yarat
    if subfolder:
        output_dir = Path(FOLDER_NAME) / subfolder
    else:
        output_dir = Path(FOLDER_NAME)
    
    return output_dir / f"{slug}.m3u8"

def save_stream(stream_config, m3u8_content):
    """m3u8 məzmununu fayla yaz"""
    slug = stream_config['slug']
    
    output_file = get_output_path(stream_config)
    output_dir = output_file.parent
    
    # Qovluğu yarat (əgər yoxdursa)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_file, 'w') as f:
            f.write(m3u8_content)
        print(f"  ✓ Saxlandı: {output_file}")
        return True
    except Exception as e:
        print(f"  ✗ Saxlana bilmədi: {e}")
        return False

def main():
    """Əsas funksiya"""
    parser = argparse.ArgumentParser(description='YouTube stream m3u8 fayllarını yenilə')
    parser.add_argument('config_files', nargs='+', help='Config fayl(lar)ı')
    parser.add_argument('--endpoint', default=ENDPOINT, help='API endpoint URL')
    parser.add_argument('--folder', default=FOLDER_NAME, help='Çıxış qovluğu')
    parser.add_argument('--timeout', type=int, default=TIMEOUT, help='Timeout saniyə')
    parser.add_argument('--retries', type=int, default=MAX_RETRIES, help='Maksimum yenidən cəhd')
    
    args = parser.parse_args()
    
    global ENDPOINT, FOLDER_NAME, TIMEOUT, MAX_RETRIES
    ENDPOINT = args.endpoint
    FOLDER_NAME = args.folder
    TIMEOUT = args.timeout
    MAX_RETRIES = args.retries
    
    print("=" * 50)
    print("TR YouTube Stream Updater")
    print("=" * 50)
    print(f"Endpoint: {ENDPOINT}")
    print(f"Çıxış qovluğu: {FOLDER_NAME}")
    print(f"Config faylları: {', '.join(args.config_files)}")
    print("=" * 50)
    
    # TR qovluğunu yarat
    tr_folder = Path(FOLDER_NAME)
    tr_folder.mkdir(exist_ok=True)
    print(f"✓ {FOLDER_NAME} qovluğu yaradıldı/yoxlanıldı")
    
    total_success = 0
    total_fail = 0
    
    for config_file in args.config_files:
        print(f"\n📄 Config işlənir: {config_file}")
        print("-" * 50)
        
        streams = load_config(config_file)
        
        for i, stream in enumerate(streams, 1):
            slug = stream.get('slug', 'unknown')
            print(f"\n[{i}/{len(streams)}] {slug}")
            
            m3u8_content, error = fetch_with_retry(stream)
            
            if m3u8_content:
                if save_stream(stream, m3u8_content):
                    total_success += 1
                else:
                    total_fail += 1
            else:
                total_fail += 1
    
    print("\n" + "=" * 50)
    print(f"Tamamlandı: {total_success} uğurlu, {total_fail} uğursuz")
    print("=" * 50)

if __name__ == "__main__":
    main()
