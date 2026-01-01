#!/usr/bin/env python3
"""
GitHub Actions üçün yt-dlp ilə YouTube M3U çıxarıcı
"""

import json
import subprocess
import os
import time
from pathlib import Path

def get_m3u_with_ytdlp(channel_id, is_video=False):
    """
    yt-dlp ilə m3u8 linki al
    """
    try:
        if is_video:
            url = f"https://www.youtube.com/watch?v={channel_id}"
        else:
            url = f"https://www.youtube.com/channel/{channel_id}/live"
        
        print(f"  📺 İşlənir: {channel_id}")
        
        # yt-dlp ilə m3u8 linkini al
        cmd = [
            'yt-dlp',
            '-g',  # Sadəcə URL ver
            '--format', 'best',
            '--no-warnings',
            '--quiet',
            '--no-check-certificate',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            m3u_url = result.stdout.strip()
            if m3u_url and m3u_url.startswith('http'):
                print(f"  ✅ M3U tapıldı")
                return m3u_url
        
        print(f"  ❌ M3U tapılmadı")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Timeout")
        return None
    except Exception as e:
        print(f"  ❌ Xəta: {str(e)[:50]}")
        return None

def save_m3u_file(slug, m3u_url, subfolder=""):
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
        
        # M3U məzmunu
        m3u_content = f"""#EXTM3U
#EXTINF:-1,{slug}
{m3u_url}"""
        
        # Faylı yaz
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        print(f"  💾 Fayl: {output_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Fayl xətası: {e}")
        return False

def main():
    print("=" * 70)
    print("🎥 GITHUB ACTIONS - YOUTUBE M3U GENERATOR")
    print("=" * 70)
    
    # yt-dlp versiyasını yoxla
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, capture_output=True)
        print("✅ yt-dlp hazırdır")
    except:
        print("⚠️ yt-dlp yoxdur, quraşdırılır...")
        os.system("pip install yt-dlp")
    
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
    
    # Hər kanal üçün
    for i, channel in enumerate(channels, 1):
        name = channel.get('name', 'N/A')
        slug = channel.get('slug', f'channel_{i}')
        channel_id = channel.get('id', '')
        channel_type = channel.get('type', 'channel')
        subfolder = channel.get('subfolder', '')
        
        if not channel_id:
            print(f"\n[{i}] ❌ ID yoxdur: {name}")
            failed += 1
            continue
        
        print(f"\n[{i}/{len(channels)}] {name}")
        
        # M3U al
        is_video = (channel_type == 'video')
        m3u_url = get_m3u_with_ytdlp(channel_id, is_video)
        
        if m3u_url:
            # Faylı yadda saxla
            if save_m3u_file(slug, m3u_url, subfolder):
                successful += 1
            else:
                failed += 1
        else:
            failed += 1
        
        # Qısa fasilə (YouTube ban etməsin)
        if i % 10 == 0:
            time.sleep(2)
        else:
            time.sleep(1)
    
    # Nəticə
    print("\n" + "=" * 70)
    print(f"✅ UĞURLU: {successful}")
    print(f"❌ UĞURSUZ: {failed}")
    print("=" * 70)
    
    # Qovluq məzmunu
    if Path("TR").exists():
        print("\n📁 TR qovluğunun məzmunu:")
        for root, dirs, files in os.walk("TR"):
            level = root.replace("TR", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                if file.endswith(".m3u8"):
                    print(f"{subindent}{file}")

if __name__ == "__main__":
    main()
