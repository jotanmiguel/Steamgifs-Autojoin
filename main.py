import os, src.session_manager as sm, argparse
from threading import local
import requests
from src import save_cookies, get_giveaways, join_giveaways
from src.config import COOKIES_PATH
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
    
    # 1. Garantir cookies guardadas
    log.info("🔍 Checking for cookies...")
    if not os.path.exists(COOKIES_PATH) and args.local:
        log.warning(f"Cookies not found at {COOKIES_PATH}. Please log in to SteamGifts and save cookies first.")
        save_cookies.save_cookies_local()

    try:
        if args.local:
            sm.start_session(local=True)
        else:
            sm.start_session(local=False)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            log.error("⚠️ Too many requests. Please wait a bit before running again.")
            return
        else:
            raise
    
    log.info("")
    
    # 2. Buscar giveaways
    giveaways = get_giveaways.fetch_giveaways()  # por ex., até 300 giveaways

    # # 4. Entrar nos giveaways
    join_giveaways.process_and_join_all(giveaways)

if __name__ == "__main__":
    main()