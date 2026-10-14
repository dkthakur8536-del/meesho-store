import re
import sys
import requests
from bs4 import BeautifulSoup

def get_telegram_api():
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Origin': 'https://my.telegram.org',
        'Referer': 'https://my.telegram.org/auth'
    }
    session.headers.update(headers)

    print("\n" + "="*45)
    print("   TELEGRAM API ID & API HASH EXTRACTOR   ")
    print("="*45 + "\n")

    # Default phone number pre-configured
    phone = "+918791443268"
    print(f"[*] Phone Number: {phone}")
    print("[*] Telegram server se OTP request bhej rahe hain...")

    try:
        resp = session.post("https://my.telegram.org/auth/send_password", data={"phone": phone}, timeout=15)
        data = resp.json()
        random_hash = data.get("random_hash")
    except Exception as e:
        print(f"[!] Request fail hui: {resp.text if 'resp' in locals() else e}")
        return

    if not random_hash:
        print(f"[!] OTP nahi bheja ja saka: {resp.text}")
        return

    # Step 2: Confirmation code input
    print("\n[+] OTP aapke Telegram app par bhej diya gaya hai.")
    web_code = input("Telegram me aaya web login code dalein: ").strip()

    print("\n[*] Login verify kiya ja raha hai...")
    login_resp = session.post(
        "https://my.telegram.org/auth/login",
        data={"phone": phone, "random_hash": random_hash, "password": web_code},
        timeout=15
    )

    if login_resp.text.strip() != "true":
        print(f"[!] Login failed! Code galat hai ya expire ho gaya: {login_resp.text}")
        return

    print("[+] Login successful! API details nikal rahe hain...")

    # Step 3: Fetch API development tools page
    apps_page = session.get("https://my.telegram.org/apps", timeout=15)
    
    # Check if app already exists
    id_match = re.search(r'api_id.*?(\d{5,})', apps_page.text, re.IGNORECASE | re.DOTALL)
    hash_match = re.search(r'api_hash.*?([a-fA-F0-9]{32})', apps_page.text, re.IGNORECASE | re.DOTALL)

    if not (id_match and hash_match):
        print("[*] Naya application register kar rahe hain...")
        soup = BeautifulSoup(apps_page.text, "html.parser")
        token = soup.find("input", {"name": "hash"})
        if token and token.get("value"):
            create_payload = {
                "hash": token.get("value"),
                "app_title": "TermuxApp",
                "app_short_name": "termuxapp",
                "app_platform": "android",
                "app_desc": "",
                "app_url": ""
            }
            session.post("https://my.telegram.org/apps/create", data=create_payload, timeout=15)
            apps_page = session.get("https://my.telegram.org/apps", timeout=15)
            id_match = re.search(r'api_id.*?(\d{5,})', apps_page.text, re.IGNORECASE | re.DOTALL)
            hash_match = re.search(r'api_hash.*?([a-fA-F0-9]{32})', apps_page.text, re.IGNORECASE | re.DOTALL)

    if id_match and hash_match:
        print("\n" + "="*45)
        print("  Aapke Telegram API Credentials:")
        print("="*45)
        print(f"API_ID   : {id_match.group(1)}")
        print(f"API_HASH : {hash_match.group(1)}")
        print("="*45 + "\n")
    else:
        print("\n[!] Automatic app create nahi ho saka (Telegram rate limit ya web security).")
        print("[*] Direct browser me https://my.telegram.org par login karke 'API development tools' se copy kar lein.")

if __name__ == "__main__":
    get_telegram_api()
