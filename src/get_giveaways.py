from datetime import timedelta
from time import time
import os
from unittest import result
from bs4 import BeautifulSoup
import json, requests, time, src.session_manager as sm
from utils.logger import log
from src.config import BASE_URL, GIVEAWAYS_FILE
from src.models import Giveaway, Giveaways
from utils.json_manager import jm


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
        g["remaining_time"] = int(end_timestamp - time.time())  # opcional, só se precisares guardar

        
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

def fetch_giveaways(max_pages=5) -> Giveaways:
    """
    Fetches giveaways from multiple pages and stores them in JSON.

    Args:
        max_pages (int, optional): Number of pages to fetch. Defaults to 5. For all pages fetch, -1 should be used.

    Returns:
        list[Giveaway]: List of Giveaway objects.
    """
    
    if max_pages == -1:
        log.info("Fetching all pages")
    
    os.makedirs(os.path.dirname(GIVEAWAYS_FILE), exist_ok=True)
    
    page = 1
    total = []
    results_len = 100
    
    while True:
        giveaways = fetch_giveaway_page(page, max_pages)
        total.extend(giveaways)
        results_len = len(giveaways)
        page += 1
        
        if max_pages != -1 and page > max_pages:
            break
        if max_pages == -1 and results_len < 100:
            break

    log.info(f"✅ Total giveaways fetched: {len(total)}")

    # converter lista de dicts → objetos Giveaway
    giveaway_objects = [Giveaway.from_dict(g) for g in total]

    # criar objeto Giveaways
    giveaways_obj = Giveaways(
        time_fetched=int(time.time()),
        results_count=len(giveaway_objects),
        giveaways={str(g.id): g for g in giveaway_objects}
    )

    # guardar usando JsonManager
    jm.write(giveaways_obj.to_dict())
    log.info(f"💾 Saved giveaways to {GIVEAWAYS_FILE} via JsonManager")
    return giveaways_obj

def sort_giveaways(
    giveaways_obj: Giveaways,
    by=("remaining_time", "points"),
    reverse=False,
    min_points=0,
    max_points=None,
    timeframe=3600
) -> list[Giveaway]:
    """
    Sorts giveaways from a Giveaways object based on specified criteria.

    Args:
        giveaways_obj (Giveaways): Giveaways object containing giveaways dict.
        by (tuple): Criteria to sort by (attributes of Giveaway).
        reverse (bool): If True, sort descending.
        min_points (int): Minimum points filter.
        max_points (int|None): Maximum points filter.
        timeframe (int|None): Filter giveaways ending within this timeframe in seconds.

    Returns:
        list[Giveaway]: Sorted list of Giveaway objects.
    """
    log.info(f"Sorting giveaways by {by}, reverse={reverse}, min_points={min_points}, max_points={max_points}, timeframe={timeframe}")

    now_ts = time.time()
    giveaways_list = list(giveaways_obj.giveaways.values())

    # aplicar filtros
    filtered = []
    for g in giveaways_list:
        if g.points < min_points:
            continue
        if max_points is not None and g.points > max_points:
            continue
        if timeframe is not None and (g.end_timestamp - now_ts) > timeframe:
            continue
        if g.joined or g.owned:
            log.debug(f"get_giveaways.sort_giveaways(): Giveaway {g.short()} already joined or owned. Skipping.")
            continue
        filtered.append(g)

    if not filtered:
        log.warning("No giveaways matched the filter criteria.")
        return []

    if isinstance(by, str):
        by = [crit.strip() for crit in by.split(",")]

    # validar atributos
    for crit in by:
        if not hasattr(filtered[0], crit):
            log.error(f"❌ Invalid sort criteria: {crit}")
            raise AttributeError(f"Giveaway has no attribute '{crit}'")

    # ordenar
    sorted_giveaways = sorted(
        filtered,
        key=lambda g: tuple(getattr(g, crit) for crit in by),
        reverse=reverse
    )

    return sorted_giveaways

if __name__ == "__main__":
    all_giveaways = fetch_giveaways()
    print(f"🎯 Total de giveaways encontrados: {len(all_giveaways)}")
