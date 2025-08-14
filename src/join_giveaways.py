from flask import g
import os, requests, time, re
import src.session_manager as sm
from src.get_giveaways import fetch_giveaway, get_link_from_id, get_giveaway_main_information
from src.config import BASE_URL
from src.models import Giveaway, Giveaways
from bs4 import BeautifulSoup
from utils.logger import log

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

def already_entered(giveaway: Giveaway, cookies):
    """_summary_

    Args:
        giveaway_id (_type_): _description_
        cookies (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    log.debug(f"Checking if already entered giveaway {giveaway.short()}...")
    resp = requests.get(giveaway.link, cookies=cookies)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Se o botão de remover existir e não tiver a classe "is-hidden", já participaste
    remove_btn = soup.find("div", {"data-do": "entry_delete"})
    if remove_btn and "is-hidden" not in remove_btn.get("class", []):
        log.warning(f"Already entered giveaway {giveaway.short()}. Skipping.")
        return True
    return False

def join_giveaway(giveaway: Giveaway):
    if not giveaway:
        log.warning(f"Giveaway not found. Skipping.")
        return False

    if giveaway.joined:
        log.info(f"Giveaway {giveaway.short()} already joined. Skipping.")
        return False

    payload = {
        "xsrf_token": sm.xsrf_token,
        "do": "entry_insert",
        "code": giveaway.code
    }

    resp = requests.post(f"{BASE_URL}/ajax.php", data=payload, cookies=sm.cookies)
    log.debug(f"Payload sent: {payload}")

    if resp.status_code == 200 and "success" in resp.text:
        log.info(f"✅ Successfully entered giveaway {giveaway.short()}.")
        giveaway.update_joined_status()
        return True
    else:
        log.error(f"❌ Failed to enter giveaway {giveaway.short()}. Response: {resp.status_code} - {resp.text}")
        return False


def process_and_join_all(giveaways: Giveaways):
    """
    Enter all the giveaways in the list.

    Args:
        giveaways (Giveaways): List of giveaways retrieved from the API.
    """
        
    log.info(f"Processing {len(giveaways)} giveaways to join...")
    total_joined = 0
    for g in giveaways:
        current_points = get_current_points()
        match current_points:
            case 0:
                log.warning("⚠️ No points available. Cannot join any giveaways.")
                break
            case _ if current_points < g.points:
                log.warning(f"⚠️ Not enough points to join giveaway {g.id}. Required: {g.points}, Available: {current_points}.")
                continue
            case _:
                if join_giveaway(g):
                    total_joined += 1
        
        time.sleep(1)  # evitar spam
    log.info(f"🎯 Total giveaways joined: {total_joined}/{len(giveaways)}")
