import re
from typing import List
from datetime import timedelta
import time
from src.config import BASE_URL
import src.session_manager as sm
from utils.logger import log
import requests
from .models import Profile, Giveaway

class ProfileService:
    def __init__(self, profile: Profile):
        self.profile = profile
        
    def current_points(self) -> int:
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
    
    
