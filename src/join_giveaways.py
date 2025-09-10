import requests, time, re
import src.session_manager as sm

from src.config import BASE_URL
from src.models import Giveaway
from utils.logger import log
from utils.json_manager import jm

def get_current_points():
    """
    Get the current points of logged user.

    Returns:
        int: Current points of the user.
        If unable to fetch points, returns 0.
    """
    
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

def is_joinable(giveaway: Giveaway, cookies) -> bool:
    log.debug(f"Checking if already entered giveaway {giveaway.short()}...")
    
    resp = requests.get(giveaway.link, cookies=cookies)
    html = resp.text

    if giveaway.joined or giveaway.owned:
        return False

    if re.search(r'data-do="entry_delete"[^>]*class="(?!.*is-hidden).*"', html):
        giveaway.update_joined_status(True)
        jm.update_giveaway(giveaway)
        return False

    if 'sidebar__error is-disabled' in html:
        giveaway.updated_owned_status(True)
        jm.update_giveaway(giveaway)
        return False

    return True

def join_giveaway(giveaway: Giveaway, cookies) -> bool:
    if not giveaway:
        log.warning("Giveaway not found. Skipping.")
        return False

    if not is_joinable(giveaway, cookies):
        log.warning(f"Giveaway {giveaway.short()} already joined or owned. Skipping.")
        return False  # já estava inscrito

    payload = {        
        "xsrf_token": sm.xsrf_token,
        "do": "entry_insert",
        "code": giveaway.code
    }

    resp = requests.post(f"{BASE_URL}/ajax.php", data=payload, cookies=sm.cookies)
    log.debug(f"Payload sent: {payload}")
    resp.raise_for_status()
    log.debug(f"Response received: {resp.text}")

    # atualizar estado
    giveaway.update_joined_status(True)
    jm.update_giveaway(giveaway)
    log.info(f"✅ Joined giveaway {giveaway.short()}")
    return True


def process_and_join_all(giveaways: list[Giveaway]):
    """
    Enter all the giveaways in the list.

    Args:
        giveaways (Giveaways): List of giveaways retrieved from the API.
    """
    
    total_joined = 0
    current_points = get_current_points()
    log.info(f"Processing {len(giveaways)} giveaways to join with {current_points}p...")
    
    for g in giveaways:
        match current_points:
            case 0:
                log.warning("⚠️ No points available. Cannot join any giveaways.")
                break
            case _ if current_points < g.points:
                log.warning(f"⚠️ Not enough points to join giveaway {g.short()}. Required: {g.points}, Available: {current_points}.")
                continue
            case _:
                if join_giveaway(g, cookies=sm.cookies):
                    current_points -= g.points
                    total_joined += 1
        
    log.info(f"🎯 Total giveaways joined: {total_joined}/{len(giveaways)}")
