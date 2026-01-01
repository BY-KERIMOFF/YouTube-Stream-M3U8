#!/usr/bin/env python3
"""
YouTube M3U Generator - Kanal ID-dən Video ID tapır
"""

import json
import subprocess
import os
import time
import re
from pathlib import Path
import requests

def get_latest_video_from_channel(channel_id):
    """
    Kanal ID-dən ən son video/canlı yayımı tap
    """
    try:
        print(f"  🔍 Kanalda video axtarılır: {channel_id}")
        
        # 1. yt-dlp ilə kanalın ən son videosunu tap
        cmd = [
            'yt-dlp',
            f'https://www.youtube.com/channel/{channel_id}',
            '--get-id',
            '--match-filter', 'is_live',
            '--no-warnings',
            '--quiet',
            '--max-downloads', '1'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0 and result.stdout.strip():
            video_id = result.stdout.strip()
            print(f"  ✅ Canlı video tapıldı: {video_id}")
            return video_id
        
        # 2. Əgər canlı yoxdursa, ən son videonu tap
        cmd2 = [
            'yt-dlp',
            f'https://www.youtube.com/channel/{channel_id}/videos',
            '--get-id',
            '--no-warnings',
            '--quiet',
            '--max-downloads', '1'
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=20)
        
        if result2.returncode == 0 and result2.stdout.strip():
            video_id = result2.stdout.strip()
            print(f"  📹 Son video tapıldı: {video_id}")
            return video_id
        
        print(f"  ❌ Heç bir video tapılmadı")
        return None
        
    except Exception as e:
        print(f"  ❌ Xəta: {str(e)[:50]}")
        return None

def get_m3u_from_video(video_id):
    """
    Video ID-dən m3u8 al
    """
    try:
        print(f"  🎬 Video işlənir: {video_id}")
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        cmd = [
            'yt-dlp',
            '-g',
            '--format', 'best[height<=720]',
            '--no-warnings',
            '--quiet',
            '--no-check-certificate',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        
        if result.returncode == 0:
            m3u_url = result.stdout.strip()
            if m3u_url and m3u_url.startswith('http'):
                print(f"  ✅ M3U tapıldı")
                return m3u_url
        
        # Alternativ cəhd
        cmd2 = [
            'yt-dlp',
            '-g',
            '--format', 'best',
            '--no-warnings',
            '--quiet',
            url
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=25)
        
        if result2.returncode == 0:
            m3u_url = result2.stdout.strip()
            if m3u_url and m3u_url.startswith('http'):
                print(f"  ✅ M3U tapıldı (alternativ)")
                return m3u_url
        
        print(f"  ❌ M3U alına bilmədi")
        return None
        
    except Exception as e:
        print(f"  ❌ Video işləmə xətası: {str(e)[:50]}")
        return None

def save_m3u_file(slug, m3u_url, subfolder="", video_title=""):
    """
    m3u8 faylını yadda saxla
    """
    try:
        if not m3u_url:
            return False
        
        # Qovluq yarat
        if subfolder:
            output_dir = Path("TR") / subfolder
        else:
            output_dir = Path("TR")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fayl adı
        output_file = output_dir / f"{slug}.m3u8"
        
        # Başlıq
        title = video_title if video_title else slug
        
        # M3U məzmunu
        m3u_content = f"""#EXTM3U
#EXTINF:-1,{title}
{m3u_url}"""
        
        # Faylı yaz
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        print(f"  💾 Fayl yaradıldı: {output_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Fayl xətası: {e}")
        return False

def get_video_title(video_id):
    """
    Video başlığını al
    """
    try:
        cmd = [
            'yt-dlp',
            '--get-title',
            '--no-warnings',
            '--quiet',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()[:100]
    except:
        pass
    return ""

def main():
    print("=" * 70)
    print("🎥 YOUTUBE KANAL → M3U KONVERTOR")
    print("=" * 70)
    
    # yt-dlp yoxla
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, capture_output=True)
        print("✅ yt-dlp hazırdır")
    except:
        print("⚠️ yt-dlp yoxdur, quraşdırılır...")
        os.system("pip install -U yt-dlp")
    
    # turkish.json yüklə
    try:
        with open('turkish.json', 'r', encoding='utf-8') as f:
            channels = json.load(f)
        print(f"📊 {len(channels)} kanal tapıldı")
    except Exception as e:
        print(f"❌ JSON xətası: {e}")
        return
    
    successful = 0
    failed = 0
    
    # TEST ÜÇÜN: İlk 10 kanalı işlə
    test_channels = channels[:20]  # Əvvəlcə 10 kanal test et
    
    print(f"\n🧪 TEST MODU: İlk {len(test_channels)} kanal işlənir...")
    
    for i, channel in enumerate(test_channels, 1):
        name = channel.get('name', 'N/A')
        slug = channel.get('slug', f'channel_{i}')
        channel_id = channel.get('id', '')
        channel_type = channel.get('type', 'channel')
        subfolder = channel.get('subfolder', '')
        
        if not channel_id:
            print(f"\n[{i}] ❌ ID yoxdur: {name}")
            failed += 1
            continue
        
        print(f"\n[{i}/{len(test_channels)}] 📺 {name}")
        
        # Əgər video tipidirsə, birbaşa işlə
        if channel_type == 'video':
            print(f"  🎬 Video ID: {channel_id}")
            m3u_url = get_m3u_from_video(channel_id)
            video_title = get_video_title(channel_id)
        else:
            # Kanal tipidirsə, əvvəlcə video tap
            video_id = get_latest_video_from_channel(channel_id)
            if video_id:
                m3u_url = get_m3u_from_video(video_id)
                video_title = get_video_title(video_id)
            else:
                m3u_url = None
                video_title = ""
        
        if m3u_url:
            # Faylı yadda saxla
            if save_m3u_file(slug, m3u_url, subfolder, video_title):
                successful += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # Fasilə ver
        time.sleep(2)
    
    # Nəticə
    print("\n" + "=" * 70)
    print(f"✅ UĞURLU: {successful}")
    print(f"❌ UĞURSUZ: {failed}")
    print("=" * 70)
    
    # Qovluq məzmunu
    if Path("TR").exists():
        print("\n📁 TR qovluğunun məzmunu:")
        m3u_files = list(Path("TR").rglob("*.m3u8"))
        for m3u_file in m3u_files[:15]:  # İlk 15 faylı göstər
            print(f"  📄 {m3u_file}")
        if len(m3u_files) > 15:
            print(f"  ... və daha {len(m3u_files) - 15} fayl")

if __name__ == "__main__":
    main()
