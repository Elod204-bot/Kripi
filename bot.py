import time
import random
import string
import re
import requests

MAIL_TM_BASE = "https://api.mail.tm"
TARGET_URL = "https://www.kripicard.com/api/register"
REF_CODE = "cmVmOjExNDc1.PPLt-heePjNCjEi9EBQuUp-8nDef6qAct4U_j8RzVTc"

def run():
    # 1. Email letrehozas (fixed domain parsing)
    res = requests.get(f"{MAIL_TM_BASE}/domains")
    data = res.json()
    
    # Handle mail.tm Hydra format or raw list
    domains = data.get('hydra:member', data) if isinstance(data, dict) else data
    domain = domains[0]['domain'] if domains else "gmail.com"
    
    user = ''.join(random.choices(string.ascii_lowercase, k=10))
    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + "A1!"
    email = f"{user}@{domain}"
    
    res = requests.post(f"{MAIL_TM_BASE}/accounts", json={"address": email, "password": pwd})
    if res.status_code != 201:
        print("Email hiba:", res.text)
        return
    print("Email:", email)

    token = requests.post(f"{MAIL_TM_BASE}/token", json={"address": email, "password": pwd}).json().get("token")

    # 2. Regisztracio
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": f"https://www.kripicard.com/register?ref={REF_CODE}"
    }
    payload = {
        "email": email,
        "password": pwd,
        "password_confirmation": pwd,
        "ref": REF_CODE
    }
    
    reg = requests.post(TARGET_URL, json=payload, headers=headers)
    print("Regisztracio valasz:", reg.status_code, reg.text)

    if reg.status_code not in [200, 201]:
        return

    # 3. Email megerosites varasa
    print("Varakozas az emailre...")
    for _ in range(12):
        time.sleep(5)
        msgs = requests.get(f"{MAIL_TM_BASE}/messages", headers={"Authorization": f"Bearer {token}"}).json()
        msg_list = msgs.get('hydra:member', msgs) if isinstance(msgs, dict) else msgs
        if msg_list:
            msg_id = msg_list[0]['id']
            content = requests.get(f"{MAIL_TM_BASE}/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"}).json().get("text", "")
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
            for u in urls:
                if "kripicard" in u or "verify" in u or "activate" in u:
                    print("Megerosito link:", u)
                    v_res = requests.get(u)
                    print("Megerosites statusz:", v_res.status_code)
                    return
    print("Nem jott meg email.")

if __name__ == "__main__":
    run()
