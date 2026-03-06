import requests
from src.config import BASE_URL
from utils.logger import log

FLARESOLVERR_URL = "http://localhost:8191/v1"

cookies = None
xsrf_token = None
session = None


def init_session():
    global cookies, xsrf_token, session

    log.info("Initializing session with FlareSolverr...")

    session = get_cloudflare_session()

    cookies = session.cookies.get_dict()

    xsrf_token = get_xsrf_token(session)

    log.info("Session initialized.")


def get_cloudflare_session():
    resp = requests.post(
        FLARESOLVERR_URL,
        json={
            "cmd": "request.get",
            "url": BASE_URL,
            "maxTimeout": 60000
        },
    )

    resp.raise_for_status()

    data = resp.json()

    s = requests.Session()

    for cookie in data["solution"]["cookies"]:
        s.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"])

    s.headers["User-Agent"] = data["solution"]["userAgent"]

    return s


def get_xsrf_token(session):
    resp = session.get(BASE_URL)
    resp.raise_for_status()

    log.info("Fetched XSRF token from main page.")

    return resp.text.split('name="xsrf_token" value="')[1].split('"')[0]
