#!/usr/bin/env python3
"""
YouTube M3U Generator - channels.json oxuyub avtomatik M3U yaradır
✨ By_Kerimoff ✨
"""

import subprocess
import json
import os
import sys
import time
import re
from datetime import datetime

def renkli_yaz(metin, renk=36):
    print(f"\033[{renk}m{metin}\033[0m")

def get_youtube_m3u(search_term):
    """YouTube axtarışından M3U URL al"""
    try:
        # Canlı yayın axtar
        cmd = [
            'yt-dlp',
            f'ytsearch1:"{search_term}"',
            '--dump-json',
            '--no-warnings',
            '--skip-download',
            '--socket-timeout', '20'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            info = json.loads(result.stdout.strip().split('\n')[0])
            video_id = info.get('id')
            is_live = info.get('is_live', False)
            
            if video_id and is_live:
                # M3U URL al
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Canlı yayın üçün format
                cmd_m3u = [
                    'yt-dlp',
                    '-g',
                    '--format', 'best[protocol^=m3u8]',
                    '--no-warnings',
                    youtube_url
                ]
                
                result_m3u = subprocess.run(cmd_m3u, capture_output=True, text=True, timeout=20)
                
                if result_m3u.returncode == 0:
                    m3u_url = result_m3u.stdout.strip()
                    if m3u_url.startswith('http'):
                        return {
                            'video_id': video_id,
                            'title': info.get('title', ''),
                            'uploader': info.get('uploader', ''),
                            'm3u_url': m3u_url.split('\n')[0],
                            'is_live': True
                        }
    except Exception as e:
        renkli_yaz(f"⚠️ Xəta: {str(e)}", 33)
    
    return None

def create_m3u_content(channel_name, video_info):
    """M3U fayl məzmunu yarat"""
    content = []
    content.append('#EXTM3U')
    content.append(f'#PLAYLIST:{channel_name}')
    content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    content.append(f'#NAME:{channel_name}')
    
    # Logo (YouTube thumbnail)
    logo_url = f"https://img.youtube.com/vi/{video_info['video_id']}/default.jpg"
    
    # Kanal məlumatı
    title = f"🔴 {channel_name} - {video_info['title'][:80]}"
    content.append(f'#EXTINF:-1 tvg-logo="{logo_url}" tvg-name="{channel_name}",{title}')
    content.append(video_info['m3u_url'])
    
    return '\n'.join(content)

def safe_filename(name):
    """Təhlükəsiz fayl adı"""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

def main():
    print("=" * 70)
    renkli_yaz("🎬 YouTube M3U Generator - By_Kerimoff", 36)
    print("=" * 70)
    
    # channels.json oxu
    try:
        with open('channels.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        renkli_yaz("❌ channels.json tapılmadı!", 31)
        sys.exit(1)
    
    channels = data.get('channels', [])
    enabled_channels = [c for c in channels if c.get('enabled', True)]
    
    renkli_yaz(f"📺 {len(enabled_channels)} kanal işlənəcək...", 32)
    
    results = []
    successful = 0
    failed = 0
    
    for i, channel in enumerate(enabled_channels, 1):
        name = channel['name']
        search = channel.get('search', f"{name} canlı yayın")
        
        print(f"\n[{i}/{len(enabled_channels)}] 📺 {name}")
        print(f"   🔍 Axtarış: {search}")
        
        # M3U URL al
        video_info = get_youtube_m3u(search)
        
        if video_info and video_info.get('m3u_url'):
            # M3U faylını yarat
            m3u_content = create_m3u_content(name, video_info)
            
            # Faylı saxla
            filename = f"m3u_files/{safe_filename(name)}.m3u"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            renkli_yaz(f"   ✅ M3U yaradıldı: {filename}", 32)
            renkli_yaz(f"   🔗 URL: {video_info['m3u_url'][:80]}...", 36)
            
            # Nəticəni saxla
            results.append({
                'name': name,
                'status': 'success',
                'file': filename,
                'video_id': video_info['video_id'],
                'title': video_info['title']
            })
            successful += 1
        else:
            renkli_yaz(f"   ❌ M3U alına bilmədi!", 31)
            results.append({
                'name': name,
                'status': 'failed'
            })
            failed += 1
        
        # Rate limit üçün gözlə
        time.sleep(2)
    
    # Nəticələri göstər
    print("\n" + "=" * 70)
    renkli_yaz("📊 NƏTİCƏLƏR", 36)
    print(f"✅ Uğurlu: {successful}")
    print(f"❌ Uğursuz: {failed}")
    print(f"📁 M3U faylları: m3u_files/ qovluğunda")
    
    # Nəticələri JSON olaraq saxla
    with open('m3u_files/results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': len(enabled_channels),
            'successful': successful,
            'failed': failed,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    # README yarat
    create_readme(results)
    
    renkli_yaz("\n✅ İŞLEM TAMAMLANDI!", 32)

def create_readme(results):
    """README faylı yarat"""
    content = []
    content.append("# 📺 YouTube M3U Kanal Listesi")
    content.append("")
    content.append(f"Son yeniləmə: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    content.append("## 🎯 İşləyən Kanallar")
    content.append("")
    
    successful = [r for r in results if r['status'] == 'success']
    
    for r in successful:
        content.append(f"### {r['name']}")
        content.append(f"- **M3U Linki**: [m3u_files/{r['file'].split('/')[-1]}](m3u_files/{r['file'].split('/')[-1]})")
        content.append(f"- **Raw URL**: https://raw.githubusercontent.com/[USERNAME]/[REPO]/main/{r['file']}")
        content.append("")
    
    content.append("## 📝 İstifadə")
    content.append("")
    content.append("1. İstədiyiniz kanalın M3U linkini kopyalayın")
    content.append("2. VLC Player → Media → Open Network Stream → Linki yapışdırın")
    content.append("3. İstənilən IPTV player-də açın")
    content.append("")
    content.append("---")
    content.append("✨ **By_Kerimoff**")
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

if __name__ == "__main__":
    main()
