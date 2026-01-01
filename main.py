#!/usr/bin/env python3
"""
TR YouTube Live Stream Updater - Enhanced Version
YouTube canlı yayınlarını avtomatik tapır və TR qovluğuna m3u8 yaradır
"""

import json
import os
import sys
import re
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Config
OUTPUT_FOLDER = 'TR'
TIMEOUT = 20
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def check_if_live(channel_id):
    """YouTube kanalının canlı yayında olub-olmadığını yoxla"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        # curl ilə səhifəni götür
        cmd = [
            'curl', '-s', '-L', '-A', USER_AGENT,
            '--compressed', '--max-time', str(TIMEOUT),
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        
        if result.returncode != 0:
            return False
        
        html = result.stdout
        
        # Canlı yayın işarələrini yoxla
        live_indicators = [
            '"isLive":true',
            '"liveStreamability"',
            'LIVE NOW',
            '正在直播',
            'Canlı Yayın',
            'liveStreamRenderer',
            'Yayında'
        ]
        
        for indicator in live_indicators:
            if indicator in html:
                return True
        
        # Əgər səhifə live səhifə deyilsə
        if '/live' not in url:
            return False
            
        return False
        
    except Exception:
        return False

def get_stream_with_ytdlp(channel_id, slug):
    """yt-dlp ilə stream URL-ni götür"""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        # Əvvəlcə canlı yayın məlumatını al
        info_cmd = [
            'yt-dlp', '-j', '--no-warnings',
            '--socket-timeout', str(TIMEOUT),
            url
        ]
        
        info_result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT + 5
        )
        
        if info_result.stdout:
            import json as json_module
            try:
                video_info = json_module.loads(info_result.stdout)
                # Video canlıdırsa
                if video_info.get('live_status') in ['is_live', 'was_live']:
                    print(f"  [LIVE] {slug} canlı yayında (yt-dlp təsdiqi)")
                    
                    # Stream URL-ni götür
                    stream_cmd = [
                        'yt-dlp', '-g', '-f', 'best[height<=720]',
                        '--no-warnings',
                        '--socket-timeout', str(TIMEOUT),
                        url
                    ]
                    
                    stream_result = subprocess.run(
                        stream_cmd,
                        capture_output=True,
                        text=True,
                        timeout=TIMEOUT
                    )
                    
                    if stream_result.stdout:
                        stream_url = stream_result.stdout.strip()
                        print(f"  [OK] Stream URL tapıldı")
                        
                        # m3u8 formatına çevir
                        m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720
{stream_url}
"""
                        return m3u8_content
                else:
                    print(f"  [OFFLINE] {slug} canlı yayında deyil")
                    return None
                    
            except Exception as e:
                print(f"  [ERROR] yt-dlp info xətası: {e}")
                return None
                
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] yt-dlp timeout")
        return None
    except Exception as e:
        print(f"  [ERROR] yt-dlp xətası: {type(e).__name__}")
        return None
    
    return None

def get_video_stream(video_id, slug):
    """Video üçün stream al"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        stream_cmd = [
            'yt-dlp', '-g', '-f', 'best[height<=720]',
            '--no-warnings',
            '--socket-timeout', str(TIMEOUT),
            url
        ]
        
        result = subprocess.run(
            stream_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        
        if result.stdout:
            stream_url = result.stdout.strip()
            print(f"  [VIDEO] Stream tapıldı")
            
            m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=1280x720
{stream_url}
"""
            return m3u8_content
            
    except Exception as e:
        print(f"  [ERROR] Video stream xətası: {e}")
    
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
        print(f"  [SAVED] {output_file}")
        
        # Fayl ölçüsünü göstər
        file_size = os.path.getsize(output_file)
        print(f"  [SIZE] {file_size} bayt")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Saxlana bilmədi: {e}")
        return False

def check_and_install_ytdlp():
    """yt-dlp yüklüdür mü yoxla"""
    try:
        subprocess.run(['yt-dlp', '--version'], 
                      capture_output=True, check=True)
        print("[OK] yt-dlp yüklüdür")
        return True
    except:
        print("[INSTALL] yt-dlp yüklənir...")
        try:
            subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'],
                          capture_output=True, check=True)
            print("[OK] yt-dlp yükləndi")
            return True
        except Exception as e:
            print(f"[ERROR] yt-dlp yüklənə bilmədi: {e}")
            return False

def process_stream(stream, index, total):
    """Tək stream-i işlə"""
    name = stream['name']
    slug = stream['slug']
    
    print(f"\n[{index}/{total}] {name}")
    print("-" * 40)
    
    # Stream tipinə görə işlə
    if stream.get('type') == 'video':
        print(f"  [TYPE] Video stream")
        content = get_video_stream(stream['id'], slug)
    else:
        # Əvvəlcə canlı olub-olmadığını yoxla
        print(f"  [CHECK] Canlı yoxlanılır...")
        is_live = check_if_live(stream['id'])
        
        if not is_live:
            print(f"  [OFFLINE] Canlı yayın yoxdur")
            
            # Köhnə faylı sil
            subfolder = stream.get('subfolder', 'genel')
            old_file = Path(OUTPUT_FOLDER) / subfolder / f"{slug}.m3u8"
            if old_file.exists():
                try:
                    old_file.unlink()
                    print(f"  [CLEAN] Köhnə fayl silindi: {old_file}")
                except:
                    pass
            return False
        
        # Canlıdırsa, stream götür
        print(f"  [LIVE] Canlı yayın tapıldı")
        content = get_stream_with_ytdlp(stream['id'], slug)
    
    if content:
        return save_m3u8(stream, content)
    else:
        print(f"  [ERROR] Stream alına bilmədi")
        return False

def main():
    """Əsas proqram"""
    print("=" * 60)
    print("TR YouTube Stream Updater - Enhanced")
    print("=" * 60)
    print(f"Başlama vaxtı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # yt-dlp yoxla
    if not check_and_install_ytdlp():
        print("[ERROR] yt-dlp olmadan davam edilə bilməz!")
        return
    
    # Config faylını yoxla
    config_file = 'turkish.json'
    if not os.path.exists(config_file):
        print(f"[ERROR] {config_file} tapılmadı!")
        return
    
    # Config oxu
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            streams = json.load(f)
        print(f"[INFO] {len(streams)} stream tapıldı")
    except Exception as e:
        print(f"[ERROR] Config oxuna bilmədi: {e}")
        return
    
    # TR qovluğunu yarat
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    
    successful = 0
    total = len(streams)
    
    print(f"\n[START] Stream-lər işlənir...")
    
    # Hər stream-i işlə
    for i, stream in enumerate(streams, 1):
        try:
            if process_stream(stream, i, total):
                successful += 1
        except Exception as e:
            print(f"  [EXCEPTION] Xəta: {type(e).__name__}")
        
        # Kiçik fasilə (rate limit üçün)
        if i % 10 == 0:
            time.sleep(1)
    
    # Nəticə
    print("\n" + "=" * 60)
    print("NƏTİCƏ")
    print("=" * 60)
    print(f"[SUCCESS] Uğurlu: {successful}")
    print(f"[FAILED] Uğursuz: {total - successful}")
    print(f"[FOLDER] Çıxış qovluğu: {OUTPUT_FOLDER}/")
    print(f"[TIME] Bitmə vaxtı: {datetime.now().strftime('%H:%M:%S')}")
    
    # Faylları göstər
    print("\n[FILES] Yaradılan fayllar:")
    try:
        m3u8_files = list(Path(OUTPUT_FOLDER).rglob('*.m3u8'))
        if m3u8_files:
            for file in sorted(m3u8_files)[:20]:  # İlk 20-ni göstər
                size = file.stat().st_size
                print(f"  [FILE] {file} ({size} bayt)")
            
            if len(m3u8_files) > 20:
                print(f"  [INFO] ... və {len(m3u8_files) - 20} daha")
        else:
            print("  [INFO] Heç bir fayl yoxdur")
    except:
        print("  [ERROR] Fayllar göstərilə bilmədi")
    
    print("=" * 60)
    
    if successful > 0:
        print("[SUCCESS] Uğurlu! Stream-lər TR qovluğuna yadda saxlanıldı.")
    else:
        print("[WARNING] Heç bir stream tapılmadı!")

if __name__ == "__main__":
    main()
