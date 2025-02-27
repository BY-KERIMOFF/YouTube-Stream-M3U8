import os

# Yeni tokenlə M3U faylı yaradılır
def create_m3u_file(token):
    m3u_content = f"#EXTM3U\n#EXTINF:-1, YouTube Live Stream\nhttps://ecanlitv3.etvserver.com/tv8.m3u8?tkn={token}&tms=1740695213\n"
    file_path = "playlist.m3u"

    # Faylı yazırıq
    with open(file_path, "w") as m3u_file:
        m3u_file.write(m3u_content)
    print(f"M3U faylı yaradıldı: {file_path}")

# Yeni tokeni alırıq
new_token = get_new_token()

if new_token:
    # Yeni tokenlə linki yaradıb çıxarırıq
    link = f"https://ecanlitv3.etvserver.com/tv8.m3u8?tkn={new_token}&tms=1740695213"
    print(f"Yeni link: {link}")

    # Yeni tokenlə M3U faylını yaradırıq
    create_m3u_file(new_token)
