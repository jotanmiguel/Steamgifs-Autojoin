import pickle
import json
import os

import dotenv
from utils.logger import log

def load_cookies(local=False, env=None, path_json="cookies/steamgifts.json"):
    """
    Retorna cookies em dict.
    - local=True: lê arquivo local (pickle ou JSON)
    - local=False: lê secret do Cloudflare (env var)
    """
    # Cloudflare / CI / produção
    if local:
        # Lê do ficheiro local
        if not os.path.exists(path_json):
            raise RuntimeError(f"Local cookies not found: {path_json}")
        with open(path_json, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Lê do Worker secret
        if not env or "COOKIES" not in env:
            raise RuntimeError("COOKIES secret not found in Cloudflare env")
        return json.loads(env["COOKIES"])
