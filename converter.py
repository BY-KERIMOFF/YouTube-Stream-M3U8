#!/usr/bin/env python3
"""
YouTube ULTIMATE M3U Converter - GitHub Auto Upload
✨ By_Kerimoff ✨
"""

import subprocess
import sys
import time
import os
import json
import requests
import re
import sqlite3
from urllib.parse import quote
import base64
from datetime import datetime

# GitHub konfiqurasiyası
CONFIG_FILE = "config.json"

def load_config():
    """Konfiqurasiya faylını yüklə"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "github_token": "",
            "github_repo": "",
            "github_branch": "main",
            "m3u_folder": "m3u_files"
        }

def save_config(config):
    """Konfiqurasiya faylını saxla"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def banner_goster():
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║     🎥 YOUTUBE M3U CONVERTER - GITHUB AUTO UPLOAD    ║
    ║                    ✨ By_Kerimoff ✨                  ║
    ║                                                       ║
    ║     Kanal Axtar | M3U Yarat | GitHub-a Yüklə        ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)

def renkli_yaz(metin, renk=36):
    print(f"\033[{renk}m{metin}\033[0m")

# ==================== GITHUB FUNCTIONS ====================

def github_upload_file(file_path, file_name, config):
    """Faylı GitHub-a yüklə"""
    if not config["github_token"] or not config["github_repo"]:
        renkli_yaz("⚠️ GitHub konfiqurasiyası edilməyib!", 33)
        return False
    
    try:
        # Faylı oxu
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Base64 encode
        encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        
        # GitHub API URL
        api_url = f"https://api.github.com/repos/{config['github_repo']}/contents/{config['m3u_folder']}/{file_name}"
        
        headers = {
            "Authorization": f"token {config['github_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Əvvəlcə faylın mövcud olub olmadığını yoxla
        response = requests.get(api_url, headers=headers)
        
        data = {
            "message": f"Add/Update M3U file: {file_name}",
            "content": encoded_content,
            "branch": config["github_branch"]
        }
        
        # Əgər fayl varsa, sha əlavə et
        if response.status_code == 200:
            existing = response.json()
            data["sha"] = existing["sha"]
            renkli_yaz(f"🔄 Mövcud fayl yenilənir: {file_name}", 33)
        else:
            renkli_yaz(f"📤 Yeni fayl yüklənir: {file_name}", 32)
        
        # Yüklə
        response = requests.put(api_url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            renkli_yaz(f"✅ GitHub-a yükləndi: {file_name}", 32)
            return True
        else:
            renkli_yaz(f"❌ Yükləmə xətası: {response.json()}", 31)
            return False
            
    except Exception as e:
        renkli_yaz(f"❌ GitHub xətası: {str(e)}", 31)
        return False

def github_create_folder_if_not_exists(config):
    """GitHub-da qovluq yarat (əgər yoxdursa)"""
    if not config["github_token"] or not config["github_repo"]:
        return False
    
    try:
        api_url = f"https://api.github.com/repos/{config['github_repo']}/contents/{config['m3u_folder']}/.gitkeep"
        headers = {
            "Authorization": f"token {config['github_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Qovluğun mövcudluğunu yoxla
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 404:
            # Qovluq yoxdur, .gitkeep faylı yarat
            data = {
                "message": "Create m3u_files folder",
                "content": base64.b64encode(b"# M3U Files Folder").decode('utf-8'),
                "branch": config["github_branch"]
            }
            response = requests.put(api_url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                renkli_yaz("✅ GitHub qovluğu yaradıldı: m3u_files", 32)
                return True
        
        return True
    except Exception as e:
        renkli_yaz(f"⚠️ Qovluq yoxlanıla bilmədi: {str(e)}", 33)
        return False

def get_github_m3u_list(config):
    """GitHub-dakı M3U fayllarının siyahısını al"""
    if not config["github_token"] or not config["github_repo"]:
        return []
    
    try:
        api_url = f"https://api.github.com/repos/{config['github_repo']}/contents/{config['m3u_folder']}"
        headers = {
            "Authorization": f"token {config['github_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            files = response.json()
            m3u_files = [f["name"] for f in files if f["name"].endswith(".m3u")]
            return m3u_files
        return []
    except:
        return []

def github_download_url(file_name, config):
    """GitHub-dan faylın raw URL-ni al"""
    if not config["github_repo"]:
        return None
    
    return f"https://raw.githubusercontent.com/{config['github_repo']}/{config['github_branch']}/{config['m3u_folder']}/{file_name}"

# ==================== YOUTUBE FUNCTIONS ====================

def youtube_search(arama_terimi):
    """YouTube axtarış"""
    try:
        cmd = [
            'yt-dlp',
            f'ytsearch5:"{arama_terimi}"',
            '--dump-json',
            '--no-warnings', 
            '--skip-download',
            '--socket-timeout', '5'
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if process.returncode == 0 and process.stdout.strip():
            videolar = []
            for line in process.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        video_info = json.loads(line)
                        video_id = video_info.get('id')
                        if video_id:
                            videolar.append({
                                'video_id': video_id,
                                'baslik': video_info.get('title', 'Bilinmir'),
                                'kanal': video_info.get('uploader', 'Bilinmir'),
                                'izleyici': video_info.get('concurrent_view_count', 0),
                                'canli': video_info.get('is_live', False),
                                'url': f"https://www.youtube.com/watch?v={video_id}"
                            })
                    except:
                        continue
            
            if videolar:
                return videolar
    except:
        pass
    
    return []

def m3u_url_al(video_id):
    """M3U URL alma"""
    try:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Video növünü yoxla
        cmd_check = [
            'yt-dlp',
            '--dump-json',
            '--no-warnings',
            '--skip-download',
            youtube_url
        ]
        
        result_check = subprocess.run(cmd_check, capture_output=True, text=True, timeout=10)
        is_live = False
        
        if result_check.returncode == 0:
            info = json.loads(result_check.stdout)
            is_live = info.get('is_live', False)
        
        # Formatları təyin et
        if is_live:
            formatlar = ['best[protocol^=m3u8]', 'best[protocol^=http]', 'best']
        else:
            formatlar = ['best[height<=720]', 'best[height<=480]', 'best']
        
        for format_str in formatlar:
            try:
                cmd = [
                    'yt-dlp',
                    '-g',
                    '--format', format_str,
                    '--no-warnings',
                    youtube_url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    m3u_url = result.stdout.strip()
                    if m3u_url and m3u_url.startswith('http'):
                        urls = m3u_url.split('\n')
                        for url in urls:
                            if url and url.startswith('http'):
                                return url.strip(), is_live
            except:
                continue
                
    except Exception as e:
        renkli_yaz(f"⚠️ M3U alma xətası: {str(e)}", 33)
    
    return None, False

def video_bilgisi_al(video_id):
    """Video məlumatları"""
    try:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-warnings',
            '--skip-download',
            youtube_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            return {
                'baslik': info.get('title', 'Bilinmir'),
                'kanal': info.get('uploader', 'Bilinmir'),
                'canli': info.get('is_live', False),
                'izleyici': info.get('concurrent_view_count', 0)
            }
    except:
        pass
    
    return None

# ==================== M3U FUNCTIONS ====================

def create_m3u_content(video_info, m3u_url):
    """M3U məzmunu yarat"""
    m3u_icerik = ['#EXTM3U']
    m3u_icerik.append(f'#PLAYLIST:{video_info["kanal"]}')
    m3u_icerik.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    m3u_icerik.append(f'#NAME:{video_info["kanal"]}')
    
    canli_icon = "🔴 " if video_info.get('canli') else ""
    baslik = f"{canli_icon}{video_info['kanal']} - {video_info['baslik'][:80]}"
    m3u_icerik.append(f'#EXTINF:-1 tvg-logo="https://img.youtube.com/vi/{video_info["video_id"]}/default.jpg",{baslik}')
    m3u_icerik.append(m3u_url)
    
    return '\n'.join(m3u_icerik)

# ==================== ANA MENU ====================

def github_ayarlari_menusu(config):
    """GitHub ayarları menüsü"""
    print("\n" + "═" * 70)
    renkli_yaz("🐙 GITHUB AYARLARI", 36)
    print(f"1. GitHub Token: {'✅ Qeyd edilib' if config['github_token'] else '❌ Qeyd edilməyib'}")
    print(f"2. Repository: {config['github_repo'] or '❌ Qeyd edilməyib'}")
    print(f"3. Branch: {config['github_branch']}")
    print(f"4. M3U Qovluğu: {config['m3u_folder']}")
    print("5. 🔙 Geri")
    print("-" * 70)
    
    secim = input("🎯 Seçim (1-5): ").strip()
    
    if secim == '1':
        token = input("🔑 GitHub Personal Access Token: ").strip()
        if token:
            config['github_token'] = token
            save_config(config)
            renkli_yaz("✅ Token qeyd edildi!", 32)
    elif secim == '2':
        repo = input("📦 Repository (istifadəçi/repo_adı): ").strip()
        if repo:
            config['github_repo'] = repo
            save_config(config)
            renkli_yaz("✅ Repository qeyd edildi!", 32)
    elif secim == '3':
        branch = input("🌿 Branch adı (default: main): ").strip() or "main"
        config['github_branch'] = branch
        save_config(config)
        renkli_yaz(f"✅ Branch qeyd edildi: {branch}", 32)
    elif secim == '4':
        folder = input("📁 M3U qovluğu adı (default: m3u_files): ").strip() or "m3u_files"
        config['m3u_folder'] = folder
        save_config(config)
        renkli_yaz(f"✅ Qovluq qeyd edildi: {folder}", 32)
    
    return config

def kanal_elave_et(config):
    """Yeni kanal əlavə et və GitHub-a yüklə"""
    print("\n" + "═" * 70)
    renkli_yaz("📺 YENİ KANAL ƏLAVƏ ET", 36)
    
    # Axtarış
    kanal_adi = input("🔍 Kanal adı: ").strip()
    if not kanal_adi:
        return
    
    renkli_yaz(f"🔍 '{kanal_adi}' axtarılır...", 36)
    videolar = youtube_search(kanal_adi + " canlı yayın")
    
    if not videolar:
        renkli_yaz("❌ Heç bir nəticə tapılmadı!", 31)
        return
    
    # Nəticələri göstər
    print(f"\n🎯 Nəticələr ({len(videolar)}):")
    print("-" * 70)
    
    for i, video in enumerate(videolar, 1):
        canli = "🔴 CANLI" if video.get('canli') else "⚫ VIDEO"
        print(f"{i}. {canli} | {video['kanal']}")
        print(f"   🎬 {video['baslik'][:70]}...")
        print()
    
    try:
        secim = int(input(f"Seçim (1-{len(videolar)}, 0 geri): "))
        if secim == 0:
            return
        
        video = videolar[secim - 1]
        
        print(f"\n⏳ M3U hazırlanır: {video['baslik'][:50]}...")
        
        # M3U URL al
        m3u_url, is_live = m3u_url_al(video['video_id'])
        
        if not m3u_url:
            renkli_yaz("❌ M3U URL alına bilmədi!", 31)
            return
        
        # Video məlumatlarını al
        video_info = video_bilgisi_al(video['video_id'])
        if not video_info:
            video_info = {
                'baslik': video['baslik'],
                'kanal': video['kanal'],
                'canli': is_live,
                'izleyici': 0
            }
        
        video_info['video_id'] = video['video_id']
        video_info['canli'] = is_live
        
        # M3U faylı yarat
        m3u_content = create_m3u_content(video_info, m3u_url)
        
        # Faylı müvəqqəti saxla
        temp_file = f"temp_{video['video_id']}.m3u"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        # GitHub-a yüklə
        if config['github_token'] and config['github_repo']:
            github_create_folder_if_not_exists(config)
            
            file_name = f"{video_info['kanal'].replace(' ', '_')}_{video['video_id']}.m3u"
            if github_upload_file(temp_file, file_name, config):
                # GitHub URL-ni göstər
                github_url = github_download_url(file_name, config)
                renkli_yaz(f"\n🔗 M3U URL: {github_url}", 36)
                
                # README üçün əlavə et
                update_readme_with_link(config, video_info, github_url)
        
        # Təmizlə
        os.remove(temp_file)
        
        renkli_yaz(f"\n✅ '{video_info['kanal']}' uğurla əlavə edildi!", 32)
        
    except ValueError:
        renkli_yaz("❌ Yanlış seçim!", 31)
    except Exception as e:
        renkli_yaz(f"❌ Xəta: {str(e)}", 31)

def update_readme_with_link(config, video_info, github_url):
    """README faylını yenilə"""
    if not config['github_token'] or not config['github_repo']:
        return
    
    try:
        # README faylını al
        api_url = f"https://api.github.com/repos/{config['github_repo']}/contents/README.md"
        headers = {
            "Authorization": f"token {config['github_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            existing = response.json()
            content = base64.b64decode(existing['content']).decode('utf-8')
            sha = existing['sha']
        else:
            content = "# YouTube M3U Kanal Listesi\n\n"
            sha = None
        
        # Yeni link əlavə et
        new_link = f"\n- [{video_info['kanal']}]({github_url}) - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        if new_link not in content:
            content += new_link
            
            # Yenilə
            data = {
                "message": f"Add channel: {video_info['kanal']}",
                "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                "branch": config['github_branch']
            }
            if sha:
                data["sha"] = sha
            
            response = requests.put(api_url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                renkli_yaz("✅ README yeniləndi!", 32)
                
    except Exception as e:
        renkli_yaz(f"⚠️ README yenilənə bilmədi: {str(e)}", 33)

def kanal_siyahisi_goster(config):
    """GitHub-dakı kanalları göstər"""
    if not config['github_token'] or not config['github_repo']:
        renkli_yaz("⚠️ Əvvəlcə GitHub ayarlarını edin!", 33)
        return
    
    renkli_yaz("📋 GitHub-dakı M3U faylları yüklənir...", 36)
    files = get_github_m3u_list(config)
    
    if not files:
        renkli_yaz("❌ Heç bir M3U faylı tapılmadı!", 31)
        return
    
    print("\n" + "═" * 70)
    renkli_yaz("📺 GITHUB M3U KANALLARI", 36)
    print(f"Toplam: {len(files)} kanal")
    print("-" * 70)
    
    for i, file in enumerate(files, 1):
        url = github_download_url(file, config)
        print(f"{i}. {file.replace('.m3u', '').replace('_', ' ')}")
        print(f"   🔗 {url}")
        print()
    
    input("🔙 Geri qayıtmaq üçün Enter basın...")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner_goster()
    
    # yt-dlp yoxla
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        renkli_yaz("✅ yt-dlp hazırdır!", 32)
    except:
        renkli_yaz("❌ yt-dlp yoxdur! Quraşdırın: pip install yt-dlp", 31)
        return
    
    # Konfiqurasiyanı yüklə
    config = load_config()
    
    while True:
        print("\n" + "═" * 70)
        renkli_yaz("🏠 ANA MENYU", 36)
        print("1. 📺 Yeni kanal əlavə et (GitHub-a yüklə)")
        print("2. 📋 GitHub-dakı kanalları göstər")
        print("3. 🐙 GitHub ayarları")
        print("4. 🚪 Çıxış")
        
        if config['github_token'] and config['github_repo']:
            renkli_yaz("✅ GitHub bağlantısı aktiv!", 32)
        
        print("-" * 70)
        
        secim = input("🎯 Seçim (1-4): ").strip()
        
        if secim == '1':
            kanal_elave_et(config)
        elif secim == '2':
            kanal_siyahisi_goster(config)
        elif secim == '3':
            config = github_ayarlari_menusu(config)
            save_config(config)
        elif secim == '4':
            renkli_yaz("\n👋 Sağ olun! By_Kerimoff", 35)
            break
        else:
            renkli_yaz("❌ Yanlış seçim!", 31)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        renkli_yaz("👋 Dayandırıldı!", 35)
    except Exception as e:
        renkli_yaz(f"\n❌ Xəta: {str(e)}", 31)
