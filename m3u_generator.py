#!/usr/bin/env python3
"""
Avtomatik M3U Playlist Generator
✨ By_Kerimoff ✨
"""

import json
import os
from datetime import datetime

print("🚀 M3U Generator başladı...")

class M3UGenerator:
    def __init__(self):
        self.data_dir = "data"
        self.public_dir = "public"
    
    def load_discovered_streams(self):
        """Kəşf edilən yayınları yüklə"""
        try:
            with open(f"{self.data_dir}/discovered_channels.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('streams', [])
        except Exception as e:
            print(f"❌ Fayl oxuma xətası: {e}")
            return []
    
    def generate_m3u_playlist(self):
        """M3U playlist yaradır"""
        print("📝 M3U playlist yaradılır...")
        
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
        
        for stream in streams:
            # Stream URL-ni al
            from auto_discover import YouTubeAutoDiscover
            discover = YouTubeAutoDiscover()
            stream_url = discover.get_stream_url(stream['video_id'])
            
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
                
                print(f"✅ Əlavə edildi: {clean_channel}")
        
        # Playlisti fayla yaz
        output_path = f"{self.public_dir}/playlist.m3u"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
        
        print(f"🎉 M3U playlist yaradıldı: {active_count} aktiv kanal")
        
        # Status faylı yarat
        status = {
            "last_update": datetime.now().isoformat(),
            "total_channels": active_count,
            "status": "success",
            "next_update": "6 hours"
        }
        
        with open(f"{self.data_dir}/status.json", "w") as f:
            json.dump(status, f, indent=2)
        
        return True

def main():
    print("🚀 M3U Generator başladı...")
    generator = M3UGenerator()
    success = generator.generate_m3u_playlist()
    
    if success:
        print("✅ M3U faylı uğurla yaradıldı!")
    else:
        print("❌ M3U faylı yaradıla bilmədi!")

if __name__ == "__main__":
    main()
