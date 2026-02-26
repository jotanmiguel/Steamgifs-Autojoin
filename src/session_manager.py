# session_manager.py
import requests, json, os
from src.config import COOKIES_PATH, BASE_URL
from utils.logger import log

cookies = None
xsrf_token = None

def init_session(local=False):
    log.info("Initializing session...")
    global cookies, xsrf_token
    cookies = get_cookies(local=local)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": BASE_URL,
    })
    session.cookies.update(cookies)
    xsrf_token = get_xsrf_token(cookies)
    log.info("Session initialized with cookies and XSRF token.")

def get_cookies(local=False, path_json=COOKIES_PATH):
    if local:
        with open(path_json, "r", encoding="utf-8") as f:
            return json.load(f)

    # ler do GitHub Actions / env
    cookies_env = os.environ.get("COOKIES")
    if cookies_env:
        return json.loads(cookies_env)

    raise RuntimeError("Cookies not found. Use local=True or set COOKIES in environment.")

def get_xsrf_token(cookies):
    resp = requests.get(BASE_URL, cookies=cookies)
    resp.raise_for_status()
    log.info("Fetched XSRF token from the main page.")
    return resp.text.split('name="xsrf_token" value="')[1].split('"')[0]
