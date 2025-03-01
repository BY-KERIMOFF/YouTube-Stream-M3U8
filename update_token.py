def update_github_repo(github_token, m3u8_link):
    if not m3u8_link:
        return "M3U8 linki tapılmadı, repo yenilənmədi."

    owner = "by-kerimoff"
    repo = "YouTube-Stream-M3U8"
    path = "xezer_tv.m3u8"
    txt_path = "xezer_tv_link.txt"  # Yeni .txt faylının adı
    github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    txt_github_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{txt_path}"

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # M3U8 faylını yeniləyirik
        response = requests.get(github_api_url, headers=headers)
        if response.status_code == 200:
            sha = response.json().get("sha")
            print(f"Fayl mövcuddur, SHA: {sha}")
        elif response.status_code == 404:
            sha = None
            print("Fayl tapılmadı, yeni fayl yaradılacaq.")
        else:
            print(f"GitHub API səhvi: {response.text}")
            return f"GitHub API səhvi: {response.text}"

        # Faylın yenilənməsi və ya yeni fayl yaradılması
        content_base64 = base64.b64encode(m3u8_link.encode()).decode()

        data = {
            "message": "Update Xezer TV M3U8 link",
            "content": content_base64,
            "sha": sha
        } if sha else {
            "message": "Add Xezer TV M3U8 link",
            "content": content_base64
        }

        # PUT sorğusu ilə fayl yenilənir
        response = requests.put(github_api_url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            print("GitHub repo M3U8 linki ilə uğurla yeniləndi.")
        else:
            print(f"GitHub API sorğusunda xəta: {response.text}")
            return f"GitHub API sorğusunda xəta: {response.text}"

        # .txt faylında M3U8 linkini qeyd edirik (müxtəlif olaraq, burada sadə mətn yazırıq)
        txt_data = {
            "message": "Add Xezer TV M3U8 link to TXT",
            "content": m3u8_link  # M3U8 linkini sadə mətn kimi göndəririk
        }

        # PUT sorğusu ilə yeni .txt fayl yaradılır və link qeyd olunur
        response_txt = requests.put(txt_github_api_url, json=txt_data, headers=headers)
        if response_txt.status_code in [200, 201]:
            print("GitHub repo-da .txt fayl ilə link uğurla qeyd edildi.")
        else:
            print(f"GitHub API sorğusunda .txt faylı xətası: {response_txt.text}")
            return f"GitHub API sorğusunda .txt faylı xətası: {response_txt.text}"

    except Exception as e:
        print(f"GitHub yeniləmə xətası: {e}")
        return f"GitHub-da xəta baş verdi: {e}"
