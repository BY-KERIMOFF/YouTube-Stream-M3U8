import re

# Yeni tokeni əldə edən funksiyanı yazırıq (Burada yeni tokeni necə əldə etdiyinizə görə dəyişə bilər)
def get_new_token():
    # Məsələn, burada yeni tokeni hardan alırsınızsa, onu əlavə edin
    new_token = "NEW_TOKEN_HERE"  # Yeni tokeni buraya daxil edin
    return new_token

# tv.txt faylını oxumaq və köhnə tokeni əvəz etmək
def replace_token_in_link():
    try:
        # tv.txt faylını oxuyuruq
        with open("tv.txt", "r") as file:
            link = file.read().strip()

        # Köhnə tokeni tapmaq üçün REGEX istifadə edirik
        old_token_match = re.search(r'tkn=([A-Za-z0-9]+)', link)
        if old_token_match:
            old_token = old_token_match.group(1)
            print(f"Köhnə token tapıldı: {old_token}")
        else:
            print("Köhnə token tapılmadı!")
            return

        # Yeni tokeni alırıq
        new_token = get_new_token()
        print(f"Yeni token: {new_token}")

        # Yeni linki hazırlayırıq
        updated_link = link.replace(f'tkn={old_token}', f'tkn={new_token}')
        print(f"Yeni link: {updated_link}")

        # Yeni linki tv.txt faylında saxlayırıq
        with open("tv.txt", "w") as file:
            file.write(updated_link)
        print("Yeni link tv.txt faylında yazıldı!")

    except FileNotFoundError:
        print("tv.txt faylı tapılmadı!")
    except Exception as e:
        print(f"Xəta baş verdi: {e}")

# Skripti işə salırıq
replace_token_in_link()
