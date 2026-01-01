#!/usr/bin/env python3
"""
TR YouTube Stream Updater - Enhanced Version
Uses webdriver-manager for automatic ChromeDriver management
"""

import json
import os
import sys
import time
import re
from pathlib import Path
from datetime import datetime

# Try to use webdriver-manager for Chrome
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Config
OUTPUT_FOLDER = 'TR'
TIMEOUT = 30

def setup_driver():
    """Setup Chrome driver with webdriver-manager"""
    if not SELENIUM_AVAILABLE:
        print("Selenium not available, using fallback method")
        return None
    
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Use webdriver-manager to automatically get ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("✅ Chrome driver setup successful")
        return driver
        
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        return None

def check_live_with_selenium(driver, channel_id, slug):
    """Check if channel is live using Selenium"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        print(f"  🔍 Checking: {slug}")
        
        driver.get(url)
        time.sleep(5)  # Allow page to load
        
        # Get page source
        page_source = driver.page_source
        
        # Check for live indicators
        live_indicators = [
            '"isLive":true',
            'LIVE',
            'Canlı',
            'ライブ',
            '正在直播',
            'liveStreamability',
            'Yayında'
        ]
        
        for indicator in live_indicators:
            if indicator in page_source:
                print(f"  ✅ Live detected")
                
                # Try to extract m3u8 URL
                m3u8_patterns = [
                    r'"hlsManifestUrl":"([^"]+)"',
                    r'https://[^"\s]+\.m3u8[^"\s]*',
                    r'manifest\.googlevideo\.com'
                ]
                
                for pattern in m3u8_patterns:
                    matches = re.findall(pattern, page_source)
                    if matches:
                        stream_url = matches[0].replace('\\', '')
                        print(f"  ✅ Stream URL found")
                        return stream_url
        
        print(f"  ❌ Not live or no stream URL")
        return None
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def get_stream_fallback(channel_id, slug):
    """Fallback method using yt-dlp"""
    try:
        import subprocess
        
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        # First check if live
        check_cmd = ['yt-dlp', '-j', '--quiet', '--no-warnings', url]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=15)
        
        if check_result.returncode != 0:
            print(f"  ❌ Channel not accessible")
            return None
        
        # Check if live
        if check_result.stdout:
            import json as json_lib
            info = json_lib.loads(check_result.stdout)
            if info.get('live_status') not in ['is_live', 'was_live']:
                print(f"  ❌ Not live")
                return None
        
        # Get stream URL
        stream_cmd = ['yt-dlp', '-g', '-f', 'best[height<=720]', '--quiet', '--no-warnings', url]
        stream_result = subprocess.run(stream_cmd, capture_output=True, text=True, timeout=20)
        
        if stream_result.returncode == 0 and stream_result.stdout.strip():
            stream_url = stream_result.stdout.strip().split('\n')[0]
            print(f"  ✅ Stream URL found (fallback)")
            return stream_url
        
        return None
        
    except Exception as e:
        print(f"  ❌ Fallback error: {e}")
        return None

def create_m3u8_content(stream_url, quality="720p"):
    """Create m3u8 file content"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720,NAME="{quality}"
{stream_url}
"""

def save_m3u8_file(slug, subfolder, content):
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
    print("TR YOUTUBE STREAM UPDATER")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Load config
    if not os.path.exists('turkish.json'):
        print("❌ ERROR: turkish.json not found!")
        return
    
    try:
        with open('turkish.json', 'r', encoding='utf-8') as f:
            streams = json.load(f)
        print(f"📋 Loaded {len(streams)} streams")
    except Exception as e:
        print(f"❌ ERROR loading config: {e}")
        return
    
    # Setup driver (if Selenium available)
    driver = None
    use_selenium = SELENIUM_AVAILABLE
    
    if use_selenium:
        print("\n🚀 Setting up Chrome driver...")
        driver = setup_driver()
        if not driver:
            print("⚠ Using fallback method only")
            use_selenium = False
    
    # Create output folder
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    # Process streams
    successful = 0
    failed = 0
    skipped = 0
    
    print(f"\n🔄 Processing {len(streams)} streams...\n")
    
    try:
        for i, stream in enumerate(streams, 1):
            name = stream['name']
            slug = stream['slug']
            stream_type = stream.get('type', 'channel')
            
            print(f"[{i:3d}/{len(streams)}] {name}")
            
            # Skip video streams for now
            if stream_type == 'video':
                print(f"     ⏭️ Video - skipped")
                skipped += 1
                continue
            
            stream_url = None
            
            # Try Selenium first
            if use_selenium and driver:
                stream_url = check_live_with_selenium(driver, stream['id'], slug)
            
            # If Selenium failed or not available, try fallback
            if not stream_url:
                stream_url = get_stream_fallback(stream['id'], slug)
            
            if not stream_url:
                print(f"     ❌ No stream available")
                failed += 1
                continue
            
            # Create and save m3u8 file
            m3u8_content = create_m3u8_content(stream_url)
            subfolder = stream.get('subfolder', 'genel')
            saved, result = save_m3u8_file(slug, subfolder, m3u8_content)
            
            if saved:
                print(f"     ✅ Saved: {result}")
                successful += 1
            else:
                print(f"     ❌ Save failed: {result}")
                failed += 1
            
            # Rate limiting
            if i % 5 == 0:
                time.sleep(1)
    
    finally:
        # Close driver if exists
        if driver:
            driver.quit()
            print("\n✅ Chrome driver closed")
    
    # Results
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed:     {failed}")
    print(f"⏭️ Skipped:    {skipped}")
    print(f"📁 Output:     {OUTPUT_FOLDER}/")
    print(f"🕒 End time:   {datetime.now().strftime('%H:%M:%S')}")
    
    # Show created files
    print(f"\n📂 Files in {OUTPUT_FOLDER}/:")
    try:
        m3u8_files = []
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                if file.endswith('.m3u8'):
                    rel_path = os.path.relpath(os.path.join(root, file), OUTPUT_FOLDER)
                    m3u8_files.append(rel_path)
        
        if m3u8_files:
            for file in sorted(m3u8_files)[:20]:
                print(f"  • {file}")
            if len(m3u8_files) > 20:
                print(f"  ... and {len(m3u8_files) - 20} more")
            print(f"\n📊 Total files: {len(m3u8_files)}")
        else:
            print("  No files created")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
