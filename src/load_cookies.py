import pickle
import json
import os
from utils.logger import log

def load_cookies(local=True, path_pickle="cookies/steamgifts.pkl", path_json="cookies/steamgifts.json"):
    """
    Retorna cookies em dict.
    - local=True: lê arquivo local (pickle ou JSON)
    - local=False: lê secret do Cloudflare
    """
    # Cloudflare
    if not local:
        cookies_json = os.environ.get("COOKIES")
        if cookies_json:
            log.info("Loading cookies from Cloudflare secret...")
            return json.loads(cookies_json)
        # fallback para JSON local
        with open(path_json, "r") as f:
            log.info(f"Loading cookies from local JSON: {path_json}")
            return json.load(f)

    # Local
    if path_pickle.endswith(".pkl") and os.path.exists(path_pickle):
        log.info(f"Loading cookies from pickle: {path_pickle}")
        with open(path_pickle, "rb") as f:
            cookies_list = pickle.load(f)
        return {c["name"]: c["value"] for c in cookies_list}

    elif path_pickle.endswith(".json") and os.path.exists(path_pickle):
        log.info(f"Loading cookies from JSON: {path_pickle}")
        with open(path_pickle, "r") as f:
            return json.load(f)

    else:
        raise FileNotFoundError(f"Cookie file not found: {path_pickle} or {path_json}")
