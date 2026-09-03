import time
import random
import string
import re
import requests

MAIL_TM_BASE = "https://api.mail.tm"
TARGET_URL = "https://www.kripicard.com/api/register"
REF_CODE = "cmVmOjExNDc1.PPLt-heePjNCjEi9EBQuUp-8nDef6qAct4U_j8RzVTc"

# Your Proxiware residential proxy configuration embedded for GitHub Actions
PROXY_URL = "http://user-yqW5klUvID2Y-network-eco:hFTxecKWZ6d1@proxy.proxiware.com:1337" 

proxies = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}

def run():
    print("[*] Proxy kapcsolat tesztelése...")
    try:
        ip_check = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
        print(f"[+] Proxy aktív! Külső IP cím: {ip_check.text}")
    except Exception as e:
        print(f"[-] Hiba a proxy csatlakozáskor: {e}")
        return

    # 1. Email letrehozas
    res = requests.get(f"{MAIL_TM_BASE}/domains", proxies=proxies, timeout=10)
    data = res.json()
    
    domains = data.get('hydra:member', data) if isinstance(data, dict) else data
    domain = domains[0]['domain'] if domains else "gmail.com"
    
    user = ''.join(random.choices(string.ascii_lowercase, k=10))
    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=12)) + "A1!"
    email = f"{user}@{domain}"
    
    res = requests.post(f"{MAIL_TM_BASE}/accounts", json={"address": email, "password": pwd}, proxies=proxies, timeout=10)
    if res.status_code != 201:
        print("Email hiba:", res.text)
        return
    print("Email létrehozva:", email)

    token = requests.post(f"{MAIL_TM_BASE}/token", json={"address": email, "password": pwd}, proxies=proxies, timeout=10).json().get("token")

    # 2. Regisztracio
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://www.kripicard.com/register?ref={REF_CODE}"
    }
    payload = {
        "email": email,
        "password": pwd,
        "password_confirmation": pwd,
        "ref": REF_CODE
    }
    
    reg = requests.post(TARGET_URL, json=payload, headers=headers, proxies=proxies, timeout=10)
    print("Regisztracio valasz statusz:", reg.status_code)
    print("Válasz szöveg (részlet):", reg.text[:200])

    if reg.status_code not in [200, 201]:
        return

    # 3. Email megerosites varasa
    print("Várakozás az e-mail megerősítésre...")
    for _ in range(12):
        time.sleep(5)
        msgs = requests.get(f"{MAIL_TM_BASE}/messages", headers={"Authorization": f"Bearer {token}"}, proxies=proxies, timeout=10).json()
        msg_list = msgs.get('hydra:member', msgs) if isinstance(msgs, dict) else msgs
        if msg_list:
            msg_id = msg_list[0]['id']
            content = requests.get(f"{MAIL_TM_BASE}/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"}, proxies=proxies, timeout=10).json().get("text", "")
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
            for u in urls:
                if "kripicard" in u or "verify" in u or "activate" in u:
                    print("Megerősítő link megtalálva:", u)
                    v_res = requests.get(u, proxies=proxies, timeout=10)
                    print("Megerősités státusz:", v_res.status_code)
                    return
    print("Nem jött meg az e-mail időben.")

if __name__ == "__main__":
    run()
