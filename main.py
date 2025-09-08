import os, src.session_manager as sm, argparse
import re
from threading import local
import requests
from src import save_cookies, get_giveaways, join_giveaways
from src.config import BASE_URL, COOKIES_PATH
from utils.logger import setup_logger, log

def main():
    parser = argparse.ArgumentParser(description="SteamGifts Autojoin Bot")
    parser.add_argument("--max-pages", type=int, default=5, help="Número máximo de páginas a buscar giveaways")
    parser.add_argument("--verbose", action="store_true", help="Ativar logs detalhados")
    parser.add_argument("--local", action="store_true", help="Usar cookies locais ao invés de Cloudflare")
    args = parser.parse_args()

    log_level = "DEBUG" if args.verbose else "INFO"
    if log_level == "DEBUG":
        setup_logger(log_level)
    else:
        setup_logger()
        
    log.info("🚀 SteamGifts Autojoin iniciado")
    
    log.info(f"Max pages to fetch: {args.max_pages}")
    
    log.info("")
    
    # Cookies e sessão
    log.info("🔍 Checking for cookies...")
    if not os.path.exists(COOKIES_PATH) and args.local:
        log.warning(f"Cookies not found at {COOKIES_PATH}. Please log in to SteamGifts and save cookies first.")
        save_cookies.save_cookies_local()

    try:
        if args.local:
            sm.init_session(local=True)
        else:
            sm.init_session(local=False)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            log.error("⚠️ Too many requests. Please wait a bit before running again.")
            return
        else:
            raise
    
    log.info("")
    
    # 2. Buscar giveaways
    giveaways = get_giveaways.fetch_giveaways()  # por ex., até 300 giveaways
    
    best_giveaways = get_giveaways.sort_giveaways(giveaways=giveaways, by=("points", "remaining_time"), max_points=current_points(), timeframe=None)

    # 4. Entrar nos giveaways
    join_giveaways.process_and_join_all(best_giveaways)
    
def current_points() -> int:
    resp = requests.get(BASE_URL, cookies=sm.cookies)
    if resp.status_code != 200:
        log.error(f"Failed to fetch current points: {resp.status_code} - {resp.text}")
        return 0
    log.debug(f"Response from {BASE_URL}: {resp.status_code} - {resp.text[:100]}...")
    log.debug("Fetching current points...")
    match = re.search(r'<span class="nav__points">(\d+)</span>', resp.text)
    if match:
        pontos = int(match.group(1))
        return pontos
    log.warning("Could not find points in the response.")
    return 0

if __name__ == "__main__":
    main()