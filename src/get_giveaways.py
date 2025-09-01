from datetime import timedelta
from time import time
import os
from bs4 import BeautifulSoup
import json, requests, time, src.session_manager as sm
from utils.logger import log
from src.config import BASE_URL, GIVEAWAYS_FILE
from src.models import Giveaway

PARAMS = {"format": "json"}

def get_link_from_id(giveaway_id: str):
    """
    Gets the giveaway link from its ID.

    Args:
        giveaway_id (str): String representing the giveaway ID.

    Returns:
        str: The URL of the giveaway.
    """
    return fetch_giveaway(giveaway_id).get("link", "")

def get_giveaway_main_information(giveaway_id: str):
    """
    Fetches the main information of a giveaway by its ID.
    """
    
    giveaway = fetch_giveaway(giveaway_id)
    
    if not giveaway:
        log.warning(f"❗ Giveaway with ID {giveaway_id} not found.")
        return None
    
    giveaway_pretty = json.dumps(giveaway, indent=4, ensure_ascii=False)
    log.info(f"🎁 Giveaway details:\n{giveaway_pretty}")
    
    return {
        "id": giveaway.get("id"),
        "title": giveaway.get("name") or giveaway.get("title"),
        "description": giveaway.get("description", ""),
        "link": giveaway.get("link"),
        "entry_count": giveaway.get("entry_count"),
    }

def fetch_giveaway_page(page=1, max_pages=5):
    """_summary_

    Args:
        page (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """
    params = PARAMS.copy()
    params["page"] = page
    log.info(f"🔍 Fetching giveaways from page {page}/{max_pages}...")    
    resp = requests.get(BASE_URL, params=params, cookies=sm.cookies)
    if resp.raise_for_status():
        log.error(f"❌ Failed to fetch giveaways from page {page}: {resp.status_code} - {resp.text}")
        return []

    data = resp.json()
    giveaways = data.get("results")
    
    log.info("🔗 Extracting giveaway codes from links...")
    for g in giveaways:
        url = g.get("link", "")
        log.debug(f"Giveaway ID: {g.get('id')}, Link: {url}")
        if url:
            g["code"] = url.split("/")[4]  # extrai o YUvtH
            log.debug(f"Extracted code from link: {g['code']}")
        else:
            g["code"] = ""
            log.warning(f"❗ Giveaway ID {g.get('id')} has no link.")
            

        end_timestamp = g.get("end_timestamp", 0)
        remaining_seconds = int(end_timestamp - time.time())

        if remaining_seconds > 0:
            days = remaining_seconds // 86400
            hours = (remaining_seconds % 86400) // 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60

            log.info(f"Remaining time: {days}d {hours:02}h:{minutes:02}m:{seconds:02}s")
            
        g["remaining_time"] = remaining_seconds
        g["remaining_time_str"] = f"{days}d {hours:02}h:{minutes:02}m:{seconds:02}s"
        
            
    log.info(f"All giveaways from page {page} fetched successfully.")
    log.info("")
    return giveaways

def fetch_giveaway(giveaway_id: str):
    
    if not os.path.exists(GIVEAWAYS_FILE):
        log.warning(f"❗ {GIVEAWAYS_FILE} não encontrado. Rodar fetch_giveaways() primeiro.")
        return fetch_giveaways()
    
    with open(GIVEAWAYS_FILE, "r", encoding="utf-8") as f:
        log.debug(f"Loading giveaways from {GIVEAWAYS_FILE}")
        giveaways = json.load(f)
    
    # procurar giveaway pelo id ou slug
    log.debug(f"Searching for giveaway with ID: {giveaway_id}")
    for g in giveaways:
        if g.get("id") == giveaway_id or g.get("slug") == giveaway_id:
            giveaway_pretty = json.dumps(g, indent=4, ensure_ascii=False)
            log.info(f"🎁 Giveaway details:\n{giveaway_pretty}")
            return g
    
    log.warning(f"❗ Giveaway with ID {giveaway_id} not found.")
    return None  # se não encontrar

def fetch_giveaways(max_pages=5):
    """
    Fetches giveaways from multiple pages and stores them in JSON.

    Args:
        max_pages (int, optional): Number of pages to fetch. Defaults to 5.

    Returns:
        list[Giveaway]: List of Giveaway objects.
    """
    
    os.makedirs(os.path.dirname(GIVEAWAYS_FILE), exist_ok=True)
    
    page = 1
    total = []
    while page <= max_pages:
        giveaways = fetch_giveaway_page(page, max_pages)
        if not giveaways:
            log.info(f"❗ No more giveaways found on page {page}. Stopping search.")
            break
        
        total.extend(giveaways)
        page += 1
        time.sleep(1)

    log.info(f"✅ Total giveaways fetched: {len(total)}")

    # Converter JSON → Objetos Giveaway
    giveaway_objects = [Giveaway.from_dict(g) for g in total]

    # Guardar no ficheiro mas usando dicionários
    with open(GIVEAWAYS_FILE, "w", encoding="utf-8") as f:
        json.dump([g.to_dict() for g in giveaway_objects], f, ensure_ascii=False, indent=4)
        log.info(f"💾 Saved giveaways to {GIVEAWAYS_FILE}")

    return giveaway_objects

def sort_giveaways(giveaways, by=("remaining_time", "points"), reverse=False, min_points=0, max_points=None, timeframe=3600):
    """
    Sorts giveaways based on specified criteria.

    Args:
        giveaways (Giveaways): List of Giveaway objects.
        by (tuple, optional): Criteria of the sort. Defaults to ("remaining_time", "points").
        reverse (bool, optional): If True, sort in descending order. Defaults to False.
        timeframe (int, optional): Timeframe in seconds to filter giveaways ending within this period. Defaults to 3600. Recomended value = same as chron function. None to disable.

    Returns:
        List: List of sorted Giveaway objects within the specified timeframe.
    """
    
    log.info(f"Sorting giveaways by {by}, reverse={reverse}, "
             f"min_points={min_points}, max_points={max_points}, timeframe={timeframe}")

    now_ts = time.time()
    filtered = []
    for g in giveaways:
        if g.points < min_points:
            continue
        if max_points is not None and g.points > max_points:
            continue
        if timeframe is not None and (g.end_timestamp - now_ts) > timeframe:
            continue
        filtered.append(g)

    if not filtered:
        log.warning("No giveaways matched the filter criteria.")
        return []

    if isinstance(by, str):
        by = [crit.strip() for crit in by.split(",")]

    for crit in by:
        if not hasattr(filtered[0], crit):
            log.error(f"❌ Invalid sort criteria: {crit}")
            raise AttributeError(f"Giveaway has no attribute '{crit}'")

    sorted_giveaways = sorted(
        filtered,
        key=lambda g: tuple(getattr(g, crit) for crit in by),
        reverse=reverse
    )

    return sorted_giveaways

if __name__ == "__main__":
    all_giveaways = fetch_giveaways()
    print(f"🎯 Total de giveaways encontrados: {len(all_giveaways)}")
