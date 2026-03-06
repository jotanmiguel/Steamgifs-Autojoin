# session_manager.py
import requests, json, os
from src.config import COOKIES_PATH, BASE_URL
from utils.logger import log
import time, requests
FLARESOLVERR_URL = os.environ.get("FLARESOLVERR_URL", "http://flaresolverr:8191/v1")

session = requests.Session()
cookies = None
xsrf_token = None

# Função para chamar FlareSolverr


def fsr_request(url, retries=5, delay=2):
    for i in range(retries):
        try:
            payload = {"cmd": "request.get", "url": url, "maxTimeout": 60000}
            resp = requests.post(FLARESOLVERR_URL, json=payload)
            resp.raise_for_status()
            return resp.json()["solution"]["response"]
        except requests.ConnectionError:
            if i < retries - 1:
                log.warning(f"FlareSolverr not ready, retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise

def init_session(local=False):
    log.info("Initializing session via FlareSolverr...")
    global cookies, xsrf_token

    cookies = get_cookies(local=local)
    # Adicionar cookies iniciais à sessão (opcional)
    session.cookies.update(cookies)

    # Pegar XSRF token usando FlareSolverr
    html = fsr_request(BASE_URL)
    xsrf_token_value = html.split('name="xsrf_token" value="')[1].split('"')[0]
    xsrf_token = xsrf_token_value

    log.info("Session initialized via FlareSolverr.")

def get_cookies(local=False, path_json=COOKIES_PATH):
    if local:
        with open(path_json, "r", encoding="utf-8") as f:
            return json.load(f)

    cookies_env = os.environ.get("COOKIES")
    if cookies_env:
        return json.loads(cookies_env)

    raise RuntimeError("Cookies not found. Use local=True or set COOKIES in environment.")

def get_xsrf_token():
    resp = session.get(BASE_URL)
    resp.raise_for_status()

    log.info("Fetched XSRF token.")
    return resp.text.split('name="xsrf_token" value="')[1].split('"')[0]