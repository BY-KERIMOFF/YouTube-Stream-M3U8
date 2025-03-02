import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_channels(url):
    """
    Verilmiş URL-dən kanalların adlarını və linklərini əldə edir.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        channels = []

        # Kanalların yerləşdiyi elementləri tapmaq
        channel_elements = soup.select('.channel-item')
        for element in channel_elements:
            name = element.select_one('.channel-name').text.strip() if element.select_one('.channel-name') else "Unknown"
            stream_url = element.select_one('a')['href'] if element.select_one('a') else None

            # Kanal məlumatlarını dictionary formasında qeyd etmək
            channel_data = {
                "name": name,
                "stream_url": stream_url
            }
            channels.append(channel_data)

        return channels

    except Exception as e:
        print(f"Xəta baş verdi: {e}")
        return []

def validate_stream_url(stream_url):
    """
    Strim URL-sinin mövcudluğunu yoxlayır.
    """
    try:
        response = requests.head(stream_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def save_to_json(data, filename="channels.json"):
    """
    Nəticəni JSON faylına yazır.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Nəticə `{filename}` faylına yazıldı.")

def main():
    url = "https://www.ecanlitvizle.app/"
    print("Kanallar yüklənir...")
    channels = fetch_channels(url)

    if not channels:
        print("Heç bir kanal tapılmadı.")
        return

    # Strim URL-lərinin doğrulanması
    validated_channels = []
    for channel in channels:
        stream_url = channel["stream_url"]
        if stream_url and validate_stream_url(stream_url):
            validated_channels.append(channel)

    if validated_channels:
        save_to_json(validated_channels)
    else:
        print("Doğru strim URL-ləri tapılmadı.")

if __name__ == "__main__":
    main()
