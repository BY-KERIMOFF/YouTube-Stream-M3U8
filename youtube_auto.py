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
import sys

class GitHubAutoM3U:
    def __init__(self):
        self.kanal_listesi = [
            # TÜRK KANALLARI
            {"ad": "SHOW TV", "id": "KpA64R5Jg-4", "ulke": "TR"},
            {"ad": "HABERTÜRK TV", "id": "qEQu1Z4Xl_4", "ulke": "TR"},
            {"ad": "CNN TÜRK", "id": "0TQZLK4kKcI", "ulke": "TR"},
            {"ad": "TRT 1", "id": "YLp6lnytp8I", "ulke": "TR"},
            {"ad": "KANAL D", "id": "gJrVMiKMSkY", "ulke": "TR"},
            {"ad": "TV8", "id": "6MvJ_gbGg_s", "ulke": "TR"},
            {"ad": "FOX TV", "id": "4t_3s02XeXo", "ulke": "TR"},
            {"ad": "ATV", "id": "3uU6E7xYd_4", "ulke": "TR"},
            {"ad": "NTV", "id": "0MFB2X3jC7E", "ulke": "TR"},
            {"ad": "TRT SPOR", "id": "k4t1t7Vq8h8", "ulke": "TR"},
            
            # BEYNELXALQ KANALLAR
            {"ad": "BBC NEWS", "id": "9Auq9mYxFEE", "ulke": "INT"},
            {"ad": "CNN INTERNATIONAL", "id": "9Auq9mYxFEE", "ulke": "INT"},
            {"ad": "AL JAZEERA", "id": "-n2VfP4o_X0", "ulke": "INT"},
            {"ad": "FRANCE 24", "id": "HeTWKNBNAas", "ulke": "INT"},
            {"ad": "SKY NEWS", "id": "9Auq9mYxFEE", "ulke": "INT"},
        ]
        
        self.m3u_dosyasi = "docs/playlist.m3u"
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
    
    def m3u_url_al(self, video_id):
        """YouTube'dan M3U URL al"""
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best[height<=720]',
                '--no-warnings',
                '--socket-timeout', '20',
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                m3u_url = result.stdout.strip()
                if m3u_url and m3u_url.startswith('http'):
                    print(f"✅ M3U URL alındı: {video_id}")
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
        
        # Veritabanında var mı?
        self.cursor.execute("SELECT m3u_url, son_yenileme FROM kanallar WHERE video_id = ?", (video_id,))
        result = self.cursor.fetchone()
        
        if result:
            m3u_url, son_yenileme = result
            # 4 saatdan azsa köhnə URL'i istifadə et
            if son_yenileme and (datetime.now() - datetime.fromisoformat(son_yenileme)).total_seconds() < 14400:
                if m3u_url and self.url_kontrol_et(m3u_url):
                    print(f"✅ Köhnə URL işləyir: {kanal_adi}")
                    return m3u_url
        
        # Yeni M3U URL al
        yeni_url = self.m3u_url_al(video_id)
        
        if yeni_url:
            # Veritabanına yaz
            self.cursor.execute('''
                INSERT OR REPLACE INTO kanallar 
                (video_id, kanal_adi, m3u_url, son_yenileme, durum, ulke)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (video_id, kanal_adi, yeni_url, datetime.now().isoformat(), "AKTIV", kanal["ulke"]))
            self.conn.commit()
            print(f"✅ Yeni URL alındı: {kanal_adi}")
            return yeni_url
        else:
            # Əgər yeni URL alına bilməzsə
            self.cursor.execute('''
                UPDATE kanallar SET durum = 'XƏTA' WHERE video_id = ?
            ''', (video_id,))
            self.conn.commit()
            print(f"❌ URL alına bilmədi: {kanal_adi}")
            return None
    
    def url_kontrol_et(self, url):
        """URL'in işlədiyini yoxla"""
        try:
            response = requests.head(url, timeout=10)
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
            time.sleep(1)  # YouTube limiti üçün
        
        return aktif_kanallar
    
    def m3u_playlist_olustur(self, kanallar):
        """M3U playlist faylı yarat"""
        m3u_icerik = ['#EXTM3U']
        m3u_icerik.append('#PLAYLIST:YouTube Canlı Yayınlar - By_Kerimoff')
        m3u_icerik.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        m3u_icerik.append(f'#TOTAL:{len(kanallar)}')
        m3u_icerik.append('#AUTO_REFRESH:4hours')
        m3u_icerik.append('#GITHUB_ACTIONS:ENABLED')
        
        for kanal in kanallar:
            if kanal["ulke"] == "TR":
                grup = "TÜRKİYE 🇹🇷"
            elif kanal["ulke"] == "INT":
                grup = "BEYNƏLXALQ 🌍"
            else:
                grup = "DİGƏR 📺"
                
            m3u_icerik.append(f'#EXTINF:-1 group-title="{grup}",{kanal["kanal"]}')
            m3u_icerik.append(kanal["url"])
        
        return '\n'.join(m3u_icerik)
    
    def m3u_dosyasi_yaz(self, icerik):
        """M3U faylını yaz"""
        # docs qovluğunu yarat
        os.makedirs("docs", exist_ok=True)
        
        with open(self.m3u_dosyasi, "w", encoding="utf-8") as f:
            f.write(icerik)
        
        print(f"✅ M3U faylı yaradıldı: {self.m3u_dosyasi}")
        
        # Status faylı da yarat
        status_icerik = f"""# 📊 YouTube M3U Status
**Son yeniləmə:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Aktiv kanallar:** {len(self.kanallari_getir())}
**Növbəti yeniləmə:** 4 saat sonra

## 📺 Kanallar:
"""
        
        for kanal in self.kanallari_getir():
            status_icerik += f"- {kanal[1]}\n"
        
        with open("docs/status.md", "w", encoding="utf-8") as f:
            f.write(status_icerik)
    
    def kanallari_getir(self):
        """Veritabanındakı kanalları getir"""
        self.cursor.execute("SELECT video_id, kanal_adi, durum FROM kanallar")
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
            
            print(f"\n🎉 TAMAMLANDI! {len(aktif_kanallar)} kanal əlavə edildi!")
            print("🌐 M3U Linki: https://kerimoff.github.io/youtube-live-m3u/playlist.m3u")
            
            # Kanalları göstər
            print("\n📊 Aktiv Kanallar:")
            for kanal in aktif_kanallar:
                print(f"  ✅ {kanal['kanal']}")
        else:
            print("❌ Heç bir kanal tapılmadı!")
        
        self.conn.close()

if __name__ == "__main__":
    auto_system = GitHubAutoM3U()
    auto_system.calistir()
