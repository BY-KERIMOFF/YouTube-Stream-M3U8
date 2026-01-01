#!/usr/bin/env python3
"""
TR YouTube Stream Updater - Direct Method
Simple and direct approach using yt-dlp
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Config
OUTPUT_FOLDER = 'TR'
TIMEOUT = 20

def get_stream_direct(channel_id, name):
    """Get stream URL directly without checking if live"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}"
        
        # Try to get any available stream (live or not)
        cmd = [
            'yt-dlp',
            '-g',  # Get URL only
            '-f', 'best',  # Best quality
            '--no-warnings',
            '--quiet',
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--socket-timeout', str(TIMEOUT),
            '--retries', '2',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        
        if result.returncode == 0 and result.stdout.strip():
            stream_url = result.stdout.strip().split('\n')[0]
            return stream_url, "Stream found"
        
        return None, "No stream"
        
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, f"Error: {e}"

def create_m3u8_content(stream_url, name):
    """Create m3u8 content"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720,NAME="{name}"
{stream_url}
"""

def save_m3u8_file(slug, subfolder, content):
    """Save m3u8 file"""
    output_dir = Path(OUTPUT_FOLDER) / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{slug}.m3u8"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Check if file has content
        if os.path.getsize(output_file) > 50:
            return True, str(output_file)
        else:
            os.remove(output_file)
            return False, "Empty file"
            
    except Exception as e:
        return False, str(e)

def update_ytdlp():
    """Update yt-dlp to latest version"""
    print("🔄 Updating yt-dlp...")
    try:
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], 
                      capture_output=True, timeout=60)
        print("✅ yt-dlp updated")
    except:
        print("⚠ Could not update yt-dlp")

def main():
    """Main function"""
    print("=" * 70)
    print("TR YOUTUBE STREAM UPDATER")
    print("=" * 70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Update yt-dlp first
    update_ytdlp()
    
    # Check config
    if not os.path.exists('turkish.json'):
        print("❌ ERROR: turkish.json not found!")
        return
    
    # Load config
    try:
        with open('turkish.json', 'r', encoding='utf-8') as f:
            streams = json.load(f)
        print(f"📋 Loaded {len(streams)} streams")
    except Exception as e:
        print(f"❌ ERROR loading config: {e}")
        return
    
    # Create output folder
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    # Process streams
    successful = 0
    failed = 0
    
    print(f"\n🔄 Processing streams (direct method)...\n")
    
    for i, stream in enumerate(streams, 1):
        name = stream['name']
        slug = stream['slug']
        
        print(f"[{i:3d}/{len(streams)}] {name}")
        
        # Skip video type for now
        if stream.get('type') == 'video':
            print(f"     ⏭️ Video - skipped")
            failed += 1
            continue
        
        # Get stream directly
        stream_url, status = get_stream_direct(stream['id'], name)
        
        if not stream_url:
            print(f"     ❌ {status}")
            failed += 1
            continue
        
        print(f"     ✅ {status}")
        
        # Create and save m3u8
        m3u8_content = create_m3u8_content(stream_url, name)
        subfolder = stream.get('subfolder', 'genel')
        saved, result = save_m3u8_file(slug, subfolder, m3u8_content)
        
        if saved:
            print(f"     💾 Saved")
            successful += 1
        else:
            print(f"     ❌ Save failed: {result}")
            failed += 1
        
        # Rate limiting
        if i % 5 == 0:
            time.sleep(2)
    
    # Results
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed:     {failed}")
    print(f"📁 Output:     {OUTPUT_FOLDER}/")
    print(f"🕒 End time:   {datetime.now().strftime('%H:%M:%S')}")
    
    # Show created files
    print(f"\n📂 Files in {OUTPUT_FOLDER}/:")
    try:
        file_count = 0
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                if file.endswith('.m3u8'):
                    if file_count < 20:
                        rel_path = os.path.relpath(os.path.join(root, file), OUTPUT_FOLDER)
                        print(f"  • {rel_path}")
                    file_count += 1
        
        if file_count > 20:
            print(f"  ... and {file_count - 20} more")
        
        print(f"\n📊 Total files: {file_count}")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print("=" * 70)
    
    if successful > 0:
        print("✅ SUCCESS: Files created in TR folder")
    else:
        print("⚠ WARNING: No files were created")

if __name__ == "__main__":
    main()
