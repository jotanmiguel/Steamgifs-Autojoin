import requests
import pickle
import os
from bs4 import BeautifulSoup

COOKIES_PATH = os.path.join("cookies", "steamgifts.pkl")
BASE_URL = "https://www.steamgifts.com"

def load_cookies():
    cookies_list = pickle.load(open(COOKIES_PATH, "rb"))
    return {c["name"]: c["value"] for c in cookies_list}

def check_login():
    cookies = load_cookies()
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(BASE_URL, cookies=cookies, headers=headers)

    soup = BeautifulSoup(resp.text, "html.parser")
    user_link = soup.find("a", class_="nav__avatar")
    if user_link:
        print("✅ Login válido como:", user_link["href"])
    else:
        print("❌ Não estás logado. Precisas gravar os cookies novamente.")

check_login()
