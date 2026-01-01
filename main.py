#!/usr/bin/env python3
"""
TR YouTube Stream Updater with Selenium
More reliable YouTube stream detection
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Config
OUTPUT_FOLDER = 'TR'

def setup_selenium():
    """Setup Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # GUI olmadan
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"Selenium setup error: {e}")
        return None

def check_channel_live(driver, channel_id, slug):
    """Check if YouTube channel is live using Selenium"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        print(f"  Checking: {slug}")
        
        driver.get(url)
        time.sleep(3)  # Saytın yüklənməsi üçün
        
        # Saytın yükləndiyini yoxla
        page_source = driver.page_source
        
        # Canlı yayın işarələrini yoxla
        live_indicators = [
            'LIVE',
            'Canlı',
            '正在直播',
            'ライブ',
            'isLive":true',
            'liveStreamability',
            'Yayında'
        ]
        
        for indicator in live_indicators:
            if indicator in page_source:
                print(f"  ✓ Live stream detected")
                return True
        
        # Daha dəqiq yoxlama - canlı badge axtar
        try:
            live_badge = driver.find_elements(By.XPATH, "//*[contains(text(), 'LIVE')]")
            if live_badge:
                print(f"  ✓ Live badge found")
                return True
        except:
            pass
        
        print(f"  ✗ Not live")
        return False
        
    except Exception as e:
        print(f"  Error checking {slug}: {e}")
        return False

def get_stream_url_with_selenium(driver, channel_id):
    """Extract stream URL from page using Selenium"""
    try:
        # Sayt mənbəsini al
        page_source = driver.page_source
        
        # m3u8 URL-lərini axtar
        import re
        patterns = [
            r'"hlsManifestUrl":"([^"]+)"',
            r'https://[^"\s]+\.m3u8[^"\s]*',
            r'https://manifest\.googlevideo\.com[^"\s]+',
            r'https://[^"\s]+\.googlevideo\.com[^"\s]+m3u8'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                stream_url = matches[0].replace('\\', '')
                print(f"  ✓ Stream URL found")
                return stream_url
        
        return None
        
    except Exception as e:
        print(f"  Error extracting stream: {e}")
        return None

def get_stream_url_fallback(channel_id):
    """Fallback method using yt-dlp"""
    try:
        import subprocess
        
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        cmd = [
            'yt-dlp',
            '-g',
            '-f', 'best',
            '--no-warnings',
            '--quiet',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        return None
    except:
        return None

def create_m3u8_content(stream_url):
    """Create m3u8 file content"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
{stream_url}
"""

def save_stream_file(slug, subfolder, content):
    """Save m3u8 content to file"""
    # Create folder
    output_dir = Path(OUTPUT_FOLDER) / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    output_file = output_dir / f"{slug}.m3u8"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, str(output_file)
    except Exception as e:
        return False, str(e)

def main():
    """Main function"""
    print("=" * 70)
    print("TR YOUTUBE STREAM UPDATER (Selenium Edition)")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Check config
    if not os.path.exists('turkish.json'):
        print("ERROR: turkish.json not found!")
        return
    
    # Load config
    try:
        with open('turkish.json', 'r', encoding='utf-8') as f:
            streams = json.load(f)
        print(f"Loaded {len(streams)} streams")
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return
    
    # Setup Selenium
    print("\n🚀 Setting up Selenium...")
    driver = setup_selenium()
    if not driver:
        print("❌ Failed to setup Selenium")
        return
    
    # Create output folder
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    # Results
    successful = 0
    failed = 0
    skipped = 0
    
    print(f"\n🔍 Checking {len(streams)} streams...\n")
    
    try:
        for i, stream in enumerate(streams, 1):
            name = stream['name']
            slug = stream['slug']
            stream_type = stream.get('type', 'channel')
            
            print(f"[{i:3d}/{len(streams)}] {name}")
            
            # Video streams skip
            if stream_type == 'video':
                print(f"     ⏭️ Video - skipped")
                skipped += 1
                continue
            
            # Check if channel is live
            is_live = check_channel_live(driver, stream['id'], slug)
            
            if not is_live:
                print(f"     ⏭️ Not live - skipped")
                skipped += 1
                continue
            
            # Get stream URL
            stream_url = None
            
            # Try Selenium first
            stream_url = get_stream_url_with_selenium(driver, stream['id'])
            
            # If Selenium fails, try yt-dlp fallback
            if not stream_url:
                print(f"     Trying fallback method...")
                stream_url = get_stream_url_fallback(stream['id'])
            
            if not stream_url:
                print(f"     ❌ Could not get stream URL")
                failed += 1
                continue
            
            # Create and save m3u8
            m3u8_content = create_m3u8_content(stream_url)
            subfolder = stream.get('subfolder', 'genel')
            saved, result = save_stream_file(slug, subfolder, m3u8_content)
            
            if saved:
                print(f"     ✅ Saved: {result}")
                successful += 1
            else:
                print(f"     ❌ Save failed")
                failed += 1
            
            # Small delay
            if i % 5 == 0:
                time.sleep(1)
    
    finally:
        # Close Selenium driver
        driver.quit()
        print("\n✅ Selenium driver closed")
    
    # Results
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed:     {failed}")
    print(f"⏭️ Skipped:    {skipped}")
    print(f"📁 Output:     {OUTPUT_FOLDER}/")
    print(f"🕒 Finished:   {datetime.now().strftime('%H:%M:%S')}")
    
    # List files
    print(f"\n📂 Files in {OUTPUT_FOLDER}/:")
    try:
        m3u8_files = []
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                if file.endswith('.m3u8'):
                    rel_path = os.path.relpath(os.path.join(root, file), OUTPUT_FOLDER)
                    m3u8_files.append(rel_path)
        
        if m3u8_files:
            for file in sorted(m3u8_files):
                print(f"  • {file}")
            print(f"\n📊 Total files: {len(m3u8_files)}")
        else:
            print("  No files created")
    except Exception as e:
        print(f"  Error listing files: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
