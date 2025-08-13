from bs4 import BeautifulSoup
import json, requests, time, src.session_manager as sm
from utils.logger import log
from src.config import BASE_URL, GIVEAWAYS_FILE

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
            
    log.info(f"All giveaways from page {page} fetched successfully.")
    log.info("")
    return giveaways

def fetch_giveaway(giveaway_id: str):
    with open("data/giveaways.json", "r", encoding="utf-8") as f:
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
    """_summary_

    Args:
        max_pages (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
    
    page = 1
    total = []
    while page <= max_pages:
        giveaways = fetch_giveaway_page(page, max_pages)
        if not giveaways:
            log.info(f"❗ No more giveaways found on page {page}. Stopping search.")
            log.info("")
            break
        
        total.extend(giveaways)
        page += 1
        time.sleep(1)
    log.info(f"✅ Total giveaways fetched: {len(total)}")
    
    log.info("")
    
    with open("data/giveaways.json", "w", encoding="utf-8") as f:
        log.info(f"💾 Saving giveaways to {GIVEAWAYS_FILE}")
        
        log.info("")
        
        json.dump(total, f, ensure_ascii=False, indent=4)
    return total

if __name__ == "__main__":
    all_giveaways = fetch_giveaways()
    print(f"🎯 Total de giveaways encontrados: {len(all_giveaways)}")
