import os
import pickle
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from src.config import COOKIES_DIR, COOKIES_FILE, FIREFOX_PATH, GECKODRIVER_PATH, BASE_URL
from utils.logger import log
import json

def save_cookies_local():
    """Abre browser para login manual e salva cookies localmente (pickle + JSON)."""
    os.makedirs(COOKIES_DIR, exist_ok=True)

    options = Options()
    options.binary_location = FIREFOX_PATH
    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(BASE_URL)
    log.info(f"🔗 Opening {BASE_URL} in browser...")
    input("👉 Faz login via Steam e pressiona ENTER quando estiver logado...")

    cookies_list = [c for c in driver.get_cookies() if "steamgifts.com" in c["domain"]]
    driver.quit()

    # Salvar em pickle
    pickle.dump(cookies_list, open(os.path.join(COOKIES_DIR, COOKIES_FILE), "wb"))
    # Salvar em JSON (para usar no Cloudflare Workers)
    with open(os.path.join(COOKIES_DIR, "steamgifts.json"), "w") as f:
        json.dump({c["name"]: c["value"] for c in cookies_list}, f, indent=2)

    log.info(f"✅ Cookies salvos em pickle e JSON no diretório {COOKIES_DIR}")
