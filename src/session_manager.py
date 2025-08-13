import pickle
import requests
from src.config import COOKIES_PATH, BASE_URL
from utils.logger import log

cookies = None
xsrf_token = None

def init_session():
    """
    Initializes the session by loading cookies and fetching the XSRF token.
    """
    global cookies, xsrf_token
    cookies = load_cookies()
    xsrf_token = get_xsrf_token(cookies)
    log.info("Session initialized with cookies and XSRF token.")

def load_cookies():
    """
    Loads cookies from the COOKIES_PATH on the config file.

    Returns:
        dict: A dictionary of cookies.
    """
    with open(COOKIES_PATH, "rb") as f:
        cookies_list = pickle.load(f)
    log.info(f"Loaded {len(cookies_list)} cookies from {COOKIES_PATH}.")
    return {c["name"]: c["value"] for c in cookies_list}

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
