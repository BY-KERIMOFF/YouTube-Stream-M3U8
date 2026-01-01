#!/usr/bin/env python3
"""
TR YouTube Stream Updater - Simple & Effective
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

def get_stream_url(source_type, source_id, slug):
    """Stream URL-ni yt-dlp ilə götür"""
    try:
        if source_type == 'channel':
            url = f"https://www.youtube.com/channel/{source_id}/live"
        else:  # video
            url = f"https://www.youtube.com/watch?v={source_id}"
        
        # 1. Əvvəlcə canlı olub-olmadığını yoxla
        check_cmd = [
            'yt-dlp', '-j', '--no-warnings',
            '--socket-timeout', '10',
            '--quiet',
            url
        ]
        
        check_result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if check_result.returncode != 0:
            return None
        
        if check_result.stdout:
            import json as json_module
            data = json_module.loads(check_result.stdout)
            
            # Əgər kanalsa və canlı deyilsə
            if source_type == 'channel' and data.get('live_status') not in ['is_live', 'was_live']:
                return None
        
        # 2. Stream URL-ni götür
        stream_cmd = [
            'yt-dlp',
            '-g',  # Stream URL-lərini götür
            '-f', 'best[height<=720]',  # 720p və ya aşağı
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
            stream_url = result.stdout.strip()
            return stream_url
        
        return None
        
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Timeout expired")
        return None
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}")
        return None

def create_m3u8_content(stream_url, quality="720p"):
    """Stream URL-dən m3u8 məzmunu yarat"""
    return f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720,NAME="{quality}"
{stream_url}
"""

def save_stream(stream_info, content):
    """Stream-i fayla yaz"""
    slug = stream_info['slug']
    subfolder = stream_info.get('subfolder', 'genel')
    
    # Qovluğu yarat
    output_dir = Path(OUTPUT_FOLDER) / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{slug}.m3u8"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, str(output_file)
    except Exception as e:
        return False, str(e)

def main():
    """Əsas funksiya"""
    print("=" * 70)
    print("TR YOUTUBE STREAM UPDATER")
    print("=" * 70)
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Config oxu
    config_file = 'turkish.json'
    if not os.path.exists(config_file):
        print(f"[ERROR] {config_file} not found!")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            streams = json.load(f)
        print(f"[INFO] Loaded {len(streams)} streams")
    except Exception as e:
        print(f"[ERROR] Could not read config: {e}")
        return
    
    # TR qovluğunu yarat
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    successful = 0
    failed = 0
    skipped = 0
    
    print(f"\n[PROCESSING] Starting stream processing...")
    
    # Hər stream üçün
    for i, stream in enumerate(streams, 1):
        name = stream['name']
        slug = stream['slug']
        stream_type = stream.get('type', 'channel')
        
        print(f"\n[{i:3d}/{len(streams)}] {name}")
        print("-" * 50)
        
        # Stream URL götür
        print(f"  [GET] Getting stream URL...")
        stream_url = get_stream_url(stream_type, stream['id'], slug)
        
        if not stream_url:
            print(f"  [SKIP] No stream available")
            
            # Köhnə faylı sil
            subfolder = stream.get('subfolder', 'genel')
            old_file = Path(OUTPUT_FOLDER) / subfolder / f"{slug}.m3u8"
            if old_file.exists():
                try:
                    old_file.unlink()
                    print(f"  [CLEAN] Removed old file")
                except:
                    pass
            
            skipped += 1
            continue
        
        print(f"  [OK] Stream URL found")
        
        # m3u8 məzmunu yarat
        m3u8_content = create_m3u8_content(stream_url)
        
        # Fayla yaz
        saved, result = save_stream(stream, m3u8_content)
        
        if saved:
            print(f"  [SAVED] {result}")
            successful += 1
        else:
            print(f"  [ERROR] Save failed: {result}")
            failed += 1
        
        # Rate limit üçün gözlə
        if i % 5 == 0:
            time.sleep(1)
    
    # Nəticə
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed:     {failed}")
    print(f"⏭️ Skipped:    {skipped}")
    print(f"📁 Output:     {OUTPUT_FOLDER}/")
    print(f"🕒 End time:   {datetime.now().strftime('%H:%M:%S')}")
    
    # Yaradılan faylları göstər
    print(f"\n📂 Created files in {OUTPUT_FOLDER}/:")
    try:
        created_files = []
        for root, dirs, files in os.walk(OUTPUT_FOLDER):
            for file in files:
                if file.endswith('.m3u8'):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, OUTPUT_FOLDER)
                    created_files.append(rel_path)
        
        if created_files:
            for file in sorted(created_files)[:15]:  # İlk 15-i göstər
                print(f"  • {file}")
            
            if len(created_files) > 15:
                print(f"  ... and {len(created_files) - 15} more")
        else:
            print("  No files created")
            
        print(f"\n📊 Total files: {len(created_files)}")
        
    except Exception as e:
        print(f"  Error listing files: {e}")
    
    print("=" * 70)
    
    if successful > 0:
        print("✅ SUCCESS: Streams saved to TR folder")
    else:
        print("⚠ WARNING: No streams were saved")

if __name__ == "__main__":
    main()
