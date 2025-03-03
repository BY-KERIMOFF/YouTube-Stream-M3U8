import requests

# AJAX sorğusunu göndərmək
ajax_url = "https://www.ecanlitvizle.app/xezer-tv-canli-izle/"  # Tokeni əldə etməli olduğumuz URL

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

try:
    # AJAX sorğusunu göndəririk
    response = requests.get(ajax_url, headers=headers)
    if response.status_code == 200:
        print("AJAX sorğusu uğurla alındı.")
        print("Cavab məzmunu:")
        print(response.text)  # Tam məzmunu çap edirik

        # JSON cavabına çevirməyi sınamaq
        try:
            json_response = response.json()
            print(json_response)
            if "token" in json_response:
                token = json_response["token"]
                print(f"Yeni token tapıldı: {token}")
            else:
                print("Token JSON içində tapılmadı.")
        except ValueError as e:
            print(f"Cavab JSON formatında deyil: {e}")

    else:
        print(f"AJAX sorğusu uğursuz oldu. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Şəbəkə problemi oldu: {e}")
