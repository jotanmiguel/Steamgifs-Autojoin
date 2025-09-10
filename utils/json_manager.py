from ast import List
from dataclasses import dataclass 
from pathlib import Path
import json
from src.models import Giveaway, Giveaways
from utils.logger import log


@dataclass
class JsonManager():
    """docstring for JsonManager."""
    
    file: str
    
    def __post_init__(self):
        """
        
        """
        path = Path(self.file)
        if path.exists():
            self.giveaways_obj = self._read()
        else:
            self.giveaways_obj = Giveaways(giveaways={})
            self.write()  # cria o ficheiro inicial
    
    def _read(self) -> Giveaways:
        with open(self.file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Giveaways.from_dict(data)
        
    def get_giveaways(self) -> dict[str, Giveaway]:
        return self.giveaways_obj.giveaways
    
    def get_giveaway(self, giveaway_id: int) -> Giveaway | None:
        data = self.giveaways_obj.giveaways.get(str(giveaway_id))
        if data:
            if isinstance(data, Giveaway):
                return data
            return Giveaway.from_dict(data)
        return None
        
    def write(self, data: Giveaways | dict) -> None:
        with open(self.file, "w", encoding="utf-8") as f:
            if isinstance(data, Giveaways):
                json.dump(data.to_dict(), f, indent=4, ensure_ascii=False)
            else:
                json.dump(data, f, indent=4, ensure_ascii=False)
    
    def update_giveaway(self, giveaway: Giveaway):
        self.giveaways_obj.giveaways[str(giveaway.id)] = giveaway
        self.write(self.giveaways_obj)
        
    def merge_giveaways(self, new_giveaways: list[Giveaway]):
        for g in new_giveaways:
            old = self.giveaways_obj.giveaways.get(str(g.id))
            if old:
                g.joined = g.joined or old.joined
                g.owned = g.owned or old.owned
            self.giveaways_obj.giveaways[str(g.id)] = g
        self.write(self.giveaways_obj)

    def cleanup_expired(self, now: float):
        before = len(self.giveaways_obj.giveaways)
        self.giveaways_obj.giveaways = {
            gid: g for gid, g in self.giveaways_obj.giveaways.items()
            if g.end_timestamp > now
        }
        after = len(self.giveaways_obj.giveaways)
        self.write(self.giveaways_obj)
        log.info(f"🧹 Cleanup: removidos {before - after} giveaways expirados.")

from src.config import DATA_FILE
jm = JsonManager(DATA_FILE)