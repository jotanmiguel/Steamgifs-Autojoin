import requests, os
from src.config import COOKIES_PATH, BASE_URL
from src.load_cookies import load_cookies
from utils.logger import log

cookies = None
xsrf_token = None
local = os.getenv("LOCAL", "False") == "True"

def init_session():
    """
    Initializes the session by loading cookies and fetching the XSRF token.
    """
    global cookies, xsrf_token
    cookies = load_cookies(local, path_pickle=COOKIES_PATH)
    xsrf_token = get_xsrf_token(cookies)
    log.info("Session initialized with cookies and XSRF token.")


def get_xsrf_token(cookies):
    """
    Fetches the XSRF token from the main page.

    Args:
        cookies (dict): The cookies to use for the request.

    Returns:
        str: The XSRF token.
    """
    resp = requests.get(BASE_URL, cookies=cookies)
    resp.raise_for_status()
    log.info("Fetched XSRF token from the main page.")
    return resp.text.split('name="xsrf_token" value="')[1].split('"')[0]
