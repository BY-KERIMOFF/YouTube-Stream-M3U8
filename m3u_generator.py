#!/usr/bin/env python3
"""
Avtomatik M3U Playlist Generator - FIXED
✨ By_Kerimoff ✨
"""

import json
import os
import sys
from datetime import datetime

print("=" * 50)
print("🚀 M3U GENERATOR BAŞLADI...")
print("=" * 50)

class M3UGenerator:
    def __init__(self):
        self.data_dir = "data"
        self.public_dir = "public"
    
    def load_discovered_streams(self):
        """Kəşf edilən yayınları yüklə"""
        try:
            file_path = f"{self.data_dir}/discovered_channels.json"
            print(f"📁 Fayl yüklənir: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            streams = data.get('streams', [])
            print(f"✅ {len(streams)} stream yükləndi")
            return streams
            
        except FileNotFoundError:
            print("❌ discovered_channels.json faylı tapılmadı!")
            return []
        except Exception as e:
            print(f"❌ Fayl oxuma xətası: {e}")
            return []
    
    def get_stream_url_direct(self, video_id):
        """Birbaşa yt-dlp ilə stream URL alır"""
        try:
            import subprocess
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Müxtəlif formatları sına
            formats_to_try = [
                'best[height<=720]',
                'best[height<=480]',
                'best',
                'worst'
            ]
            
            for fmt in formats_to_try:
                try:
                    cmd = [
                        'yt-dlp',
                        '-g',
                        '--format', fmt,
                        '--no-warnings',
                        '--socket-timeout', '20',
                        url
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
                    
                    if result.returncode == 0:
                        stream_url = result.stdout.strip()
                        if stream_url and stream_url.startswith('http'):
                            return stream_url
                            
                except:
                    continue
            
            return None
                    
        except Exception as e:
            print(f"  ❌ Stream URL xətası {video_id}: {str(e)}")
            return None
    
    def generate_m3u_playlist(self):
        """M3U playlist yaradır"""
        print("📝 M3U PLAYLIST YARADILIR...")
        
        streams = self.load_discovered_streams()
        
        if not streams:
            print("❌ Heç bir canlı yayın tapılmadı!")
            # Əlcə minimum playlist yarat
            return self.create_minimal_playlist()
        
        m3u_content = ['#EXTM3U']
        m3u_content.append('#PLAYLIST:YouTube Canlı Yayınlar - AVTOMATİK')
        m3u_content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        m3u_content.append(f'#TOTAL:{len(streams)}')
        m3u_content.append('#AUTO_UPDATE:6 hours')
        m3u_content.append('#BY:Kerimoff')
        m3u_content.append('#SOURCE:AUTO_DISCOVERY')
        
        active_count = 0
        
        print(f"🔄 {len(streams)} stream üçün URL-lər alınır...")
        
        for i, stream in enumerate(streams, 1):
            print(f"  [{i}/{len(streams)}] {stream.get('channel', 'Bilinmeyen')}...")
            
            stream_url = self.get_stream_url_direct(stream['video_id'])
            
            if stream_url:
                # Xüsusi simvolları təmizlə
                title = stream.get('title', 'Bilinməyən')
                channel = stream.get('channel', 'Bilinməyən')
                
                clean_title = title.replace(',', '').replace('#', '').strip()
                clean_channel = channel.replace(',', '').replace('#', '').strip()
                
                # M3U entry yarat
                m3u_content.append(f'#EXTINF:-1 tvg-id="{stream["video_id"]}" tvg-name="{clean_channel}",{clean_channel} - {clean_title}')
                m3u_content.append(stream_url)
                active_count += 1
                
                print(f"  ✅ ƏLAVƏ EDİLDİ: {clean_channel}")
            else:
                print(f"  ❌ STREAM YOXDUR: {stream.get('channel', 'Bilinmeyen')}")
        
        # Əgər heç bir stream işləmirsə, minimal playlist yarat
        if active_count == 0:
            print("⚠️ Heç bir stream işləmir, minimal playlist yaradılır...")
            return self.create_minimal_playlist()
        
        # Playlisti fayla yaz
        output_path = f"{self.public_dir}/playlist.m3u"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
        
        print(f"\n🎉 M3U PLAYLIST YARADILDI: {active_count} AKTİV KANAL")
        print(f"📁 Fayl: {output_path}")
        
        # Status faylı yarat
        status = {
            "last_update": datetime.now().isoformat(),
            "total_channels": active_count,
            "status": "success",
            "next_update": "6 hours"
        }
        
        with open(f"{self.data_dir}/status.json", "w") as f:
            json.dump(status, f, indent=2)
        
        print(f"💾 Status faylı yaradıldı: data/status.json")
        
        return True
    
    def create_minimal_playlist(self):
        """Minimal işləyən playlist yaradır"""
        print("🔧 Minimal playlist yaradılır...")
        
        minimal_streams = [
            {
                'video_id': 'KpA64R5Jg-4',
                'title': 'SHOW TV Canlı Yayın',
                'channel': 'SHOW TV'
            },
            {
                'video_id': 'qEQu1Z4Xl_4',
                'title': 'HABERTÜRK TV Canlı Yayın', 
                'channel': 'HABERTÜRK TV'
            },
            {
                'video_id': '0TQZLK4kKcI',
                'title': 'CNN TÜRK Canlı Yayın',
                'channel': 'CNN TÜRK'
            }
        ]
        
        m3u_content = ['#EXTM3U']
        m3u_content.append('#PLAYLIST:YouTube Canlı Yayınlar - MINIMAL')
        m3u_content.append(f'#GENERATED:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        m3u_content.append('#STATUS:MINIMAL_FALLBACK')
        m3u_content.append('#BY:Kerimoff')
        
        active_count = 0
        
        for stream in minimal_streams:
            stream_url = self.get_stream_url_direct(stream['video_id'])
            if stream_url:
                m3u_content.append(f'#EXTINF:-1 tvg-id="{stream["video_id"]}" tvg-name="{stream["channel"]}",{stream["channel"]} - {stream["title"]}')
                m3u_content.append(stream_url)
                active_count += 1
                print(f"  ✅ MINIMAL: {stream['channel']}")
        
        output_path = f"{self.public_dir}/playlist.m3u"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
        
        print(f"🎉 MINIMAL PLAYLIST YARADILDI: {active_count} KANAL")
        return True

def main():
    print("🚀 M3U Generator başladı...")
    generator = M3UGenerator()
    success = generator.generate_m3u_playlist()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ M3U FAYLI UĞURLA YARADILDI!")
    else:
        print("❌ M3U FAYLI YARADILA BİLMƏDİ!")
    print("=" * 50)

if __name__ == "__main__":
    main()
