#!/usr/bin/env python3
"""
Avtomatik M3U Playlist Generator
✨ By_Kerimoff ✨
"""

import json
import os
import sys
from datetime import datetime

print("=" * 50)
print("🚀 M3U GENERATOR BAŞLADI...")
print("=" * 50)

# AutoDiscover modulunu əlavə et
sys.path.append('.')

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
    
    def get_stream_url(self, video_id):
        """Canlı yayın URL-ni alır (birbaşa yt-dlp ilə)"""
        try:
            import subprocess
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            cmd = [
                'yt-dlp',
                '-g',
                '--format', 'best[height<=720]',
                '--no-warnings',
                '--socket-timeout', '15',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url and stream_url.startswith('http'):
                    return stream_url
                    
        except Exception as e:
            print(f"  ❌ Stream URL xətası {video_id}: {str(e)}")
        
        return None
    
    def generate_m3u_playlist(self):
        """M3U playlist yaradır"""
        print("📝 M3U PLAYLIST YARADILIR...")
        
        streams = self.load_discovered_streams()
        
        if not streams:
            print("❌ Heç bir canlı yayın tapılmadı!")
            return False
        
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
            print(f"  [{i}/{len(streams)}] {stream['channel']}...")
            
            stream_url = self.get_stream_url(stream['video_id'])
            
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
                print(f"  ❌ STREAM YOXDUR: {stream['channel']}")
        
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
