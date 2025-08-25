# session_manager.py
import requests, json, os
from src.config import COOKIES_PATH, BASE_URL
from utils.logger import log

# Variáveis globais da sessão
cookies = None
xsrf_token = None

def init_session(local=False, env=None):
    """
    Inicializa a sessão carregando cookies e buscando XSRF token.
    
    Args:
        local (bool): Se True, lê cookies do ficheiro local.
        env (dict): Objeto env do Cloudflare Worker (para acessar secrets).
    """
    log.info("Initializing session...")
    global cookies, xsrf_token
    cookies = get_cookies(local=local, env=env)
    xsrf_token = get_xsrf_token(cookies)
    log.info("Session initialized with cookies and XSRF token.")

def get_cookies(local=False, env=None, path_json=COOKIES_PATH):
    """
    Obtém cookies como dict.
    
    - local=True: lê ficheiro local JSON
    - local=False: lê secret do Cloudflare a partir de 'env'
    """
    if local:
        if not os.path.exists(path_json):
            log.error(f"Cookie file not found: {path_json}")
            raise FileNotFoundError(f"Cookie file not found: {path_json}")
        log.info(f"Loading cookies from local JSON: {path_json}")
        with open(path_json, "r", encoding="utf-8") as f:
            return json.load(f)

    if env:
        cookies_json = env.get("COOKIES")
        if cookies_json:
            log.info("Loading cookies from Cloudflare secret...")
            return json.loads(cookies_json)

    raise RuntimeError("Cookies not found. Use local=True or ensure COOKIES secret is defined in env.")

def get_xsrf_token(cookies):
    """
    Busca o XSRF token da página principal.

    Args:
        cookies (dict): Cookies para a request.

    Returns:
        str: XSRF token
    """
    resp = requests.get(BASE_URL, cookies=cookies)
    resp.raise_for_status()
    log.info("Fetched XSRF token from the main page.")
    return resp.text.split('name="xsrf_token" value="')[1].split('"')[0]
