# config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
BIN_DIR = os.path.join(BASE_DIR, "bin")
COOKIES_DIR = os.path.join(BASE_DIR, "cookies")
COOKIES_FILE = "steamgifts.json"
COOKIES_PATH = os.path.join(COOKIES_DIR, COOKIES_FILE)
GECKODRIVER_PATH = os.path.join(BIN_DIR, "geckodriver.exe")
BASE_URL = "https://www.steamgifts.com"
FIREFOX_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"  # <-- ajustar se necessário
GIVEAWAYS_FILE = os.path.join(BASE_DIR, "data", "giveaways.json")
