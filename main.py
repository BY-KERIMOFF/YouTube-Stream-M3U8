#!/usr/bin/env python3
"""
TR YouTube Stream Updater - Simple & Effective
Uses only yt-dlp for maximum reliability
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
TIMEOUT = 25

def get_stream_info(channel_id, slug):
    """Get stream information using yt-dlp"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        # 1. First get video info to check if live
        info_cmd = [
            'yt-dlp',
            '-j',  # JSON output
            '--no-warnings',
            '--quiet',
            '--socket-timeout', '15',
            url
        ]
        
        info_result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if info_result.returncode != 0:
            return None, "Channel not accessible"
        
        # Parse JSON response
        import json as json_lib
        try:
            video_info = json_lib.loads(info_result.stdout)
        except:
            return None, "Invalid response"
        
        # Check if live
        live_status = video_info.get('live_status')
        if live_status not in ['is_live', 'was_live']:
            return None, "Not live"
        
        # 2. Get stream URL
        stream_cmd = [
            'yt-dlp',
            '-g',  # Get direct URL
            '-f', 'best[height<=720]/best',  # Prefer 720p
            '--no-warnings',
            '--quiet',
            '--socket-timeout', str(TIMEOUT),
            url
        ]
        
        stream_result = subprocess.run(
            stream_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        
        if stream_result.returncode != 0:
            return None, "No stream URL"
        
        if not stream_result.stdout.strip():
            return None, "Empty response"
        
        # Get first URL (usually the stream URL)
        stream_url = stream_result.stdout.strip().split('\n')[0]
        
        # Additional info
        title = video_info.get('title', 'Unknown')
        return stream_url, f"Live: {title}"
        
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, f"Error: {type(e).__name__}"

def get_video_stream(video_id, slug):
    """Get stream for a specific video"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        stream_cmd = [
            'yt-dlp',
            '-g',
            '-f', 'best[height<=720]/best',
            '--no-warnings',
            '--quiet',
            '--socket-timeout', str(TIMEOUT),
            url
        ]
        
        result = subprocess.run(
            stream_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        
        if result.returncode == 0 and result.stdout.strip():
            stream_url = result.stdout.strip().split('\n')[0]
            return stream_url, "Video stream"
        
        return None, "No stream"
        
    except Exception as e:
        return None, f"Error: {e}"

def create_m3u8_content(stream_url, name="Stream"):
    """Create m3u8 file content"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720,NAME="{name}"
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
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
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
    skipped = 0
    
    print(f"\n🔄 Processing streams...\n")
    
    for i, stream in enumerate(streams, 1):
        name = stream['name']
        slug = stream['slug']
        stream_type = stream.get('type', 'channel')
        
        print(f"[{i:3d}/{len(streams)}] {name}")
        
        # Get stream based on type
        stream_url = None
        status = ""
        
        if stream_type == 'channel':
            stream_url, status = get_stream_info(stream['id'], slug)
        else:  # video
            stream_url, status = get_video_stream(stream['id'], slug)
        
        if not stream_url:
            print(f"     ❌ {status}")
            
            # Remove old file if exists
            subfolder = stream.get('subfolder', 'genel')
            old_file = Path(OUTPUT_FOLDER) / subfolder / f"{slug}.m3u8"
            if old_file.exists():
                try:
                    old_file.unlink()
                    print(f"     🗑️ Removed old file")
                except:
                    pass
            
            failed += 1
            continue
        
        print(f"     ✅ {status}")
        
        # Create and save m3u8
        m3u8_content = create_m3u8_content(stream_url, name)
        subfolder = stream.get('subfolder', 'genel')
        saved, result = save_m3u8_file(slug, subfolder, m3u8_content)
        
        if saved:
            print(f"     💾 Saved: {os.path.basename(result)}")
            successful += 1
        else:
            print(f"     ❌ Save failed: {result}")
            failed += 1
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
    
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
        import os
        file_count = 0
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                if file.endswith('.m3u8'):
                    if file_count < 20:  # Show first 20
                        rel_path = os.path.relpath(os.path.join(root, file), OUTPUT_FOLDER)
                        print(f"  • {rel_path}")
                    file_count += 1
        
        if file_count > 20:
            print(f"  ... and {file_count - 20} more")
        
        print(f"\n📊 Total files: {file_count}")
        
    except Exception as e:
        print(f"  Error listing files: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
