import pickle
import json
import os

COOKIES_DIR = "cookies"
COOKIES_FILE = "steamgifts.pkl"
JSON_FILE = "steamgifts.json"

# 1. Carregar o pickle
with open(os.path.join(COOKIES_DIR, COOKIES_FILE), "rb") as f:
    cookies_list = pickle.load(f)

# 2. Converter para dict simples {name: value}
cookies_dict = {c["name"]: c["value"] for c in cookies_list if "steamgifts.com" in c["domain"]}

# 3. Salvar em JSON
with open(os.path.join(COOKIES_DIR, JSON_FILE), "w") as f:
    json.dump(cookies_dict, f, indent=2)

print(f"✅ Cookies salvos em JSON: {os.path.join(COOKIES_DIR, JSON_FILE)}")
