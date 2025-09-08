from ast import List
from dataclasses import dataclass
from pathlib import Path
import json
from src.models import Giveaway, Giveaways

BASE_DIR = Path(__file__).parent.parent  # project_root
DATA_DIR = BASE_DIR / "data"
DATA_FILE = BASE_DIR / "data" / "giveaways.json"

@dataclass
class JsonManager():
    """docstring for JsonManager."""
    
    file: str
    
    def read(self) -> Giveaways:
        with open(self.file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Giveaways.from_dict(data)
        
    def write(self, data: Giveaway) -> None:
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    def get_giveaways(self) -> Giveaways:
        giveaways = self.read().giveaways
        return giveaways
            
    def get_giveaway(self, giveaway_id: int) -> Giveaway | None:
        giveaways = self.get_giveaways()
        data = giveaways.get(str(giveaway_id))
        if data:
            # Se já for Giveaway, retorna direto
            if isinstance(data, Giveaway):
                return data
            # Se for dict cru (fallback raro)
            return Giveaway.from_dict(data)
        return None

    
    def update_giveaway(self, giveaway: Giveaway) -> None:
        giveaways_obj: Giveaways = self.read()
        
        giveaways_obj.giveaways[str(giveaway.id)] = giveaway
        
        self.write(giveaways_obj.to_dict())
