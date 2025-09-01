from dataclasses import dataclass, asdict
from datetime import timedelta
import re
import time
from typing import Any, List, Optional, Dict
from utils.logger import log
import requests
from src.config import BASE_URL
import src.session_manager as sm

@dataclass
class Creator:
    """
    Class representing a creator of a giveaway.

    Attributes:
        id (int): The ID of the creator.
        steam_id (str): The Steam ID of the creator.
        username (str): The username of the creator.

    Returns:
        dict: Creator object as a dictionary.
    """
    id: int
    steam_id: str
    username: str

    def to_dict(self) -> Dict[str, any]:
        return asdict(self)

@dataclass
class Giveaway:
    id: int
    name: str
    points: int
    copies: int
    app_id: Optional[int] = None
    package_id: Optional[int] = None
    link: str = ""
    created_timestamp: int = 0
    start_timestamp: int = 0
    end_timestamp: int = 0
    comment_count: int = 0
    entry_count: int = 0
    creator: Optional[Creator] = None
    code: str = ""
    
    region_restricted: bool = False
    invite_only: bool = False
    whitelist: bool = False
    group: bool = False
    contributor_level: int = 0
    joined: bool = False
    score: float = 0.0
    remaining_time: int = 0
    remaining_time_str: str = ""      

    def to_dict(self) -> Dict[str, any]:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Giveaway":
        creator_data = data.get("creator")
        creator = Creator(**creator_data) if creator_data else None
        return Giveaway(
            id=data["id"],
            name=data["name"],
            points=data.get("points", 0),
            copies=data.get("copies", 1),
            app_id=data.get("app_id"),
            package_id=data.get("package_id"),
            link=data.get("link", ""),
            created_timestamp=data.get("created_timestamp", 0),
            start_timestamp=data.get("start_timestamp", 0),
            end_timestamp=data.get("end_timestamp", 0),
            region_restricted=data.get("region_restricted", False),
            invite_only=data.get("invite_only", False),
            whitelist=data.get("whitelist", False),
            group=data.get("group", False),
            contributor_level=data.get("contributor_level", 0),
            comment_count=data.get("comment_count", 0),
            entry_count=data.get("entry_count", 0),
            creator=creator,
            code=data.get("code", ""),
            joined=data.get("joined", False),
            remaining_time=data.get("remaining_time", 0),
            remaining_time_str=data.get("remaining_time_str", ""),     
            score=data.get("score", 0)  
        )

    def update_joined_status(self):
        self.entry_count = self.entry_count + 1 if self.joined == False else self.entry_count - 1
        self.joined = True if self.joined else False
    
    def timedelta(self) -> timedelta:
        return timedelta(self.end_timestamp - time.time())
    
    def get_probability(self):
        if self.joined:
            return 1/(self.entry_count/self.copies)
        else:
            return 1/(self.entry_count+1/self.copies)
        
    def __str__(self):
        return (
            f"🎁 {self.name} (ID: {self.id})\n"
            f"   🔗 Link: {self.link}\n"
            f"   🏷️ Points: {self.points} | Copies: {self.copies} | Entries: {self.entry_count} | Probability: {self.get_probability():.2f}\n"
            f"   👤 Creator: {self.creator.username if self.creator else 'Unknown'}\n"
            f"   🕒 Ends in: {self.remaining_time_str}"
        )

    def short(self) -> str:
        return f"🎁 {self.name} - {self.link}"

    def __repr__(self):
        return f"<Giveaway {self.name} ({self.id}) ({self.link})- Points: {self.points}, Remaining: {self.remaining_time_str}"

@dataclass
class Giveaways:
    giveaways: List[Giveaway]

    def __iter__(self):
        return iter(self.giveaways)

    def to_dict(self) -> List[Dict[str, Any]]:
        return [g.to_dict() for g in self.giveaways]
    
@dataclass
class Profile:
    username: str
    user_id: int
    level: int
    points: int
    giveaways_count: int
    wins_count: int
    comments_count: int
    created_timestamp: int

    def to_dict(self) -> Dict[str, any]:
        return asdict(self)