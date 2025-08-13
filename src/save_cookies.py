import os
import pickle
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from src.config import COOKIES_DIR, COOKIES_PATH, FIREFOX_PATH, GECKODRIVER_PATH, COOKIES_FILE, BASE_URL
from utils.logger import log

def save_cookies():
    """Abre o browser para login manual e guarda cookies no ficheiro indicado."""
    os.makedirs(COOKIES_DIR, exist_ok=True)

    options = Options()
    options.binary_location = FIREFOX_PATH
    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(BASE_URL)
    log.info(f"🔗 Opening {BASE_URL} in the browser...")
    log.info(f"🔗 Login to {BASE_URL} and press ENTER after successful login...")
    input(f"Login into {BASE_URL} and press ENTER to continue...")
    log.info("🔒 Storing cookies...")
    pickle.dump(driver.get_cookies(), open(os.path.join(COOKIES_DIR, COOKIES_FILE), "wb"))
    driver.quit()
    log.info("Leaving the browser...")
    log.info(f"✅ Cookies saved to {os.path.join(COOKIES_DIR, COOKIES_FILE)}")
    
def load_cookies():
    """Carrega cookies do ficheiro e devolve um dict pronto para requests."""
    cookies_path = os.path.join(COOKIES_DIR, COOKIES_FILE)
    if not os.path.exists(cookies_path):
        log.error(f"Cookies file not found: {cookies_path}")
        raise FileNotFoundError(f"Cookies file not found: {cookies_path}")
    
    log.info(f"🔍 Loading cookies from {cookies_path}...")

    with open(cookies_path, "rb") as f:
        cookies_list = pickle.load(f)
    if not cookies_list:
        log.error("No cookies found in the file.")
        raise ValueError("No cookies found in the file.")
    log.info(f"✅ Loaded {len(cookies_list)} cookies from {cookies_path}")
    log.debug(f"Cookies: {cookies_list}")
    
    # Converter lista de dicts em dict simples
    cookies_dict = {c["name"]: c["value"] for c in cookies_list}
    log.info("Cookies converted to dict format for requests.")
    return cookies_dict

if __name__ == "__main__":
    save_cookies("https://store.steampowered.com/login/", "steam.pkl")
