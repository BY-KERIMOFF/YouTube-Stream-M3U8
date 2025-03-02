import re
import requests

# tv.txt faylını oxumaq
with open('tv.txt', 'r') as file:
    content = file.read()

# Tokeni tapmaq üçün regex istifadə etmək
old_token_match = re.search(r'tkn=([A-Za-z0-9]+)', content)

if old_token_match:
    old_token = old_token_match.group(1)
    print(f"Köhnə token tapıldı: {old_token}")

    # Burada yeni tokeni əldə etməlisiniz. (Məsələn, bir API-dən və ya başqa bir mənbədən)
    # Bu misalda biz sadəcə 'NEW_TOKEN_HERE' istifadə edirik.
    new_token = 'NEW_TOKEN_HERE'

    # Yeni link yaratmaq
    new_link = content.replace(f'tkn={old_token}', f'tkn={new_token}')
    print(f"Yeni link: {new_link}")

    # Yeni linki tv.txt faylında yazmaq
    with open('tv.txt', 'w') as file:
        file.write(new_link)
    print("Yeni link tv.txt faylında yazıldı!")
else:
    print("Token tapılmadı!")
