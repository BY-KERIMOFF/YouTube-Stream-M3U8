#!/usr/bin/env python3
"""
YouTube CANLI YAYIN M3U Generator - GITHUB AVTOMATIK VERSION
✨ By_Kerimoff ✨
🔄 GITHUB ACTIONS ILE 7/24 CALISIR
"""

import os
import json
import requests
import subprocess
import sqlite3
from datetime import datetime
import time
import re

class GitHubAutoM3U:
    def __init__(self):
        # YENİLƏNİŞ VİDEO ID-LƏRİ
        self.kanal_listesi = [
            # TÜRK KANALLARI - YENİ ID-LƏR
            {"ad": "SHOW TV", "id": "lweJapMIdcQ", "ulke": "TR"},
            {"ad": "HABERTÜRK TV", "id": "BeH7n1I6kC4", "ulke": "TR"},
            {"ad": "CNN TÜRK", "id": "0TQZLK4kKcI", "ulke": "TR"},
            {"ad": "TRT 1", "id": "0t4P18-9UuU", "ulke": "TR"},
            {"ad": "KANAL D", "id": "q6M2CxJXh_c", "ulke": "TR"},
            {"ad": "TV8", "id": "6MvJ_gbGg_s", "ulke": "TR"},
            {"ad": "FOX TV", "id": "4t_3s02XeXo", "ulke": "TR"},
            {"ad": "BEYAZ TV", "id": "a9qL7v5Q8zA", "ulke": "TR"},
            {"ad": "NTV", "id": "0MFB2X3jC7E", "ulke": "TR"},
            {"ad": "TRT SPOR", "id": "k4t1t7Vq8h8", "ulke": "TR"},
            
            # BEYNELXALQ KANALLAR - CANLI YAYIN ID-LƏRİ
            {"ad": "BBC NEWS", "id": "wNz2lJN4YB8", "ulke": "INT"},
            {"ad": "CNN INTERNATIONAL", "id": "9Auq9mYxFEE", "ulke": "INT"},
            {"ad": "AL JAZEERA ENGLISH", "id": "-n2VfP4o_X0", "ulke": "INT"},
            {"ad": "FRANCE 24 ENGLISH", "id": "HeTWKNBNAas", "ulke": "INT"},
            {"ad": "DW NEWS", "id": "2n3DGk8YIoE", "ulke": "INT"},
            
            # MUSIQI KANALLARI
            {"ad": "NRJ HITS", "id": "y6M-sE7BS2A", "ulke": "MUSIC"},
            {"ad": "TRT MÜZİK", "id": "n4M6zUq3L_g", "ulke": "MUSIC"},
        ]
        
        self.m3u_dosyasi = "playlist.m3u"
        self.veritabani = "youtube_streams.db"
        self.baglanti_olustur()
    
    def baglanti_olustur(self):
        """SQLite veritabanı bağlantısı"""
        self.conn = sqlite3.connect(self.veritabani)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kanallar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                kanal_adi TEXT,
                m3u_url TEXT,
                son_yenileme TIMESTAMP,
                durum TEXT,
                ulke TEXT
            )
        ''')
        self.conn.commit()
    
    def youtube_search_live(self, arama_terimi):
        """YouTube-da canlı yayın axtar"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={arama_terimi.replace(' ', '+')}+canlı"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Video ID-ləri tap
                video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
                unique_ids = list(dict.fromkeys(video_ids))
                
                for video_id in unique_ids[:3]:  # İlk 3 nəticə
                    # Bu video canlı yayındırmı?
                    if self.is_live_stream(video_id):
                        return video_id
                        
        except Exception as e:
            print(f"❌ Axtarış xətası: {e}")
        
        return None
    
    def is_live_stream(self, video_id):
        """Video canlı yayındırmı?"""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '--skip-download',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return info.get('is_live', False)
                
        except:
            pass
        
        return False
    
    def m3u_url_al(self, video_id):
        """YouTube-dan M3U URL al - YENİ ÜSUL"""
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # ƏVVƏLCƏ sadə yt-dlp
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best',
                '--no-warnings',
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            
            if result.returncode == 0:
                m3u_url = result.stdout.strip()
                if m3u_url and m3u_url.startswith('http'):
                    print(f"✅ M3U URL alındı: {video_id}")
                    return m3u_url
            
            # ƏGƏR OLMAZSA, alternativ format
            cmd2 = [
                'yt-dlp',
                '-g',
                '--format', 'worst',
                '--no-warnings',
                youtube_url
            ]
            
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=25)
            if result2.returncode == 0:
                m3u_url = result2.stdout.strip()
                if m3u_url and m3u_url.startswith('http'):
                    print(f"✅ Alternativ M3U URL alındı: {video_id}")
                    return m3u_url
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout: {video_id}")
        except Exception as e:
            print(f"❌ M3U alma xətası ({video_id}): {str(e)}")
        
        return None
    
    def kanal_kontrol_et(self, kanal):
        """Kanalı kontrol et və M3U al"""
        video_id = kanal["id"]
        kanal_adi = kanal["ad"]
        
        print(f"🔍 Kontrol edilir: {kanal_adi}")
        
        # ƏVVƏLCƏ veritabanında yoxla
        self.cursor.execute("SELECT m3u_url, son_yenileme FROM kanallar WHERE video_id = ?", (video_id,))
        result = self.cursor.fetchone()
        
        if result:
            m3u_url, son_yenileme = result
            # 6 saatdan azsa köhnə URL'i istifadə et
            if son_yenileme and (datetime.now() - datetime.fromisoformat(son_yenileme)).total_seconds() < 21600:
                if m3u_url and self.url_kontrol_et(m3u_url):
                    print(f"✅ Köhnə URL işləyir: {kanal_adi}")
                    return m3u_url
        
        # YENİ M3U URL al
        yeni_url = self.m3u_url_al(video_id)
        
        if not yeni_url:
            # ƏGƏR M3U ALINMASA, yeni canlı yayın axtar
            print(f"🔄 {kanal_adi} üçün yeni canlı yayın axtarılır...")
            yeni_video_id = self.youtube_search_live(kanal_adi)
            
            if yeni_video_id:
                print(f"🎯 Yeni canlı yayın tapıldı: {yeni_video_id}")
                yeni_url = self.m3u_url_al(yeni_video_id)
                if yeni_url:
                    # Yeni video_id ilə yenilə
                    video_id = yeni_video_id
        
        if yeni_url:
            # Veritabanına yaz
            self.cursor.execute('''
                INSERT OR REPLACE INTO kanallar 
                (video_id, kanal_adi, m3u_url, son_yenileme, durum, ulke)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (video_id, kanal_adi, yeni_url, datetime.now().isoformat(), "AKTIV", kanal["ulke"]))
            self.conn.commit()
            print(f"✅ URL əlavə edildi: {kanal_adi}")
            return yeni_url
        else:
            # Əgər URL alına bilməzsə
            self.cursor.execute('''
                UPDATE kanallar SET durum = 'XƏTA' WHERE video_id = ?
            ''', (video_id,))
            self.conn.commit()
            print(f"❌ URL alına bilmədi: {kanal_adi}")
            return None
    
    def url_kontrol_et(self, url):
        """URL'in işlədiyini yoxla"""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def tum_kanallari_kontrol_et(self):
        """Bütün kanalları kontrol et"""
        print("🔄 Bütün kanallar kontrol edilir...")
        aktif_kanallar = []
        
        for kanal in self.kanal_listesi:
            m3u_url = self.kanal_kontrol_et(kanal)
            if m3u_url:
                aktif_kanallar.append({
                    "kanal": kanal["ad"],
                    "url": m3u_url,
                    "ulke": kanal["ulke"]
                })
            time.sleep(2)  # YouTube limiti üçün
        
        return aktif_kanallar
    
    def m3u_playlist_olustur(self, kanallar):
        """M3U playlist faylı yarat"""
        m3u_icerik = ['#EXTM3U']
        m3u_icerik.append('#PLAYLIST:YouTube Canlı Yayınlar - By_Kerimoff')
        m3u_icerik.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        m3u_icerik.append(f'#TOTAL:{len(kanallar)}')
        m3u_icerik.append('#AUTO_REFRESH:6hours')
        m3u_icerik.append('#GITHUB_ACTIONS:ENABLED')
        
        for kanal in kanallar:
            if kanal["ulke"] == "TR":
                grup = "TÜRKİYE 🇹🇷"
            elif kanal["ulke"] == "INT":
                grup = "BEYNƏLXALQ 🌍"
            else:
                grup = "MUSİQİ 🎵"
                
            m3u_icerik.append(f'#EXTINF:-1 group-title="{grup}",{kanal["kanal"]}')
            m3u_icerik.append(kanal["url"])
        
        return '\n'.join(m3u_icerik)
    
    def m3u_dosyasi_yaz(self, icerik):
        """M3U faylını yaz"""
        with open(self.m3u_dosyasi, "w", encoding="utf-8") as f:
            f.write(icerik)
        
        print(f"✅ M3U faylı yaradıldı: {self.m3u_dosyasi}")
        
        # Status faylı da yarat
        status_icerik = f"""# 📊 YouTube M3U Status
**Son yeniləmə:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Aktiv kanallar:** {len(self.kanallari_getir())}
**Növbəti yeniləmə:** 6 saat sonra

## 📺 Kanallar:
"""
        
        kanallar = self.kanallari_getir()
        for kanal in kanallar:
            status_icerik += f"- {kanal[1]} - {kanal[2]}\\n"
        
        with open("status.md", "w", encoding="utf-8") as f:
            f.write(status_icerik)
    
    def kanallari_getir(self):
        """Veritabanındakı kanalları getir"""
        self.cursor.execute("SELECT video_id, kanal_adi, durum FROM kanallar WHERE durum = 'AKTIV'")
        return self.cursor.fetchall()
    
    def calistir(self):
        """Əsas işləmə funksiyası"""
        print("🚀 YouTube Auto M3U Generator Başladı!")
        print("✨ By_Kerimoff - GitHub Actions Version")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Kanal kontrolü
        aktif_kanallar = self.tum_kanallari_kontrol_et()
        
        # M3U yarat
        if aktif_kanallar:
            m3u_icerik = self.m3u_playlist_olustur(aktif_kanallar)
            self.m3u_dosyasi_yaz(m3u_icerik)
            
            print(f"\\n🎉 TAMAMLANDI! {len(aktif_kanallar)} kanal əlavə edildi!")
            print("🌐 M3U Linki: https://raw.githubusercontent.com/kerimoff/youtube-live-m3u/main/playlist.m3u")
            
            # Kanalları göstər
            print("\\n📊 Aktiv Kanallar:")
            for kanal in aktif_kanallar:
                print(f"  ✅ {kanal['kanal']}")
        else:
            # Əgər heç bir kanal tapılmasa, nümunə M3U yarat
            print("⚠️ Heç bir kanal tapılmadı, nümunə M3U yaradılır...")
            ornek_kanallar = [
                {"kanal": "SHOW TV", "url": "https://example.com/showtv.m3u8", "ulke": "TR"},
                {"kanal": "TRT 1", "url": "https://example.com/trt1.m3u8", "ulke": "TR"},
            ]
            m3u_icerik = self.m3u_playlist_olustur(ornek_kanallar)
            self.m3u_dosyasi_yaz(m3u_icerik)
            print("✅ Nümunə M3U faylı yaradıldı")
        
        self.conn.close()

if __name__ == "__main__":
    auto_system = GitHubAutoM3U()
    auto_system.calistir()
