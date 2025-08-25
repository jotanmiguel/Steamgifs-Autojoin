import pickle
import json
import os
from utils.logger import log

def load_cookies(local=False, path_pickle="cookies/steamgifts.pkl", path_json="cookies/steamgifts.json"):
    """
    Retorna cookies em dict.
    - local=True: lê arquivo local (pickle ou JSON)
    - local=False: lê secret do Cloudflare (env var)
    """
    # Cloudflare / CI / produção
    if not local:
        cookies_json = os.environ.get("COOKIES")
        if cookies_json:
            log.info("Using Env cookies...")
            return json.loads(cookies_json)
        else:
            # fallback apenas local, se existir ficheiro JSON
            if os.path.exists(path_json):
                log.info(f"Env COOKIES not found. Using local JSON: {path_json}")
                with open(path_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            raise ValueError("COOKIES env variable not found and local JSON does not exist.")

    # Local
    if path_pickle.endswith(".pkl") and os.path.exists(path_pickle):
        log.info(f"Loading cookies from pickle: {path_pickle}")
        with open(path_pickle, "rb") as f:
            cookies_list = pickle.load(f)
        return {c["name"]: c["value"] for c in cookies_list}

    elif path_pickle.endswith(".json") and os.path.exists(path_pickle):
        log.info(f"Loading cookies from JSON: {path_pickle}")
        with open(path_pickle, "r", encoding="utf-8") as f:
            return json.load(f)

    else:
        raise FileNotFoundError(f"Cookie file not found: {path_pickle} or {path_json}")
