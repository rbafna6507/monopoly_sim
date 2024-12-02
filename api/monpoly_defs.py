from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Property:
    name: str
    position: int
    price: int
    rent: List[int]  # [base, 1 house, 2 houses, 3 houses, 4 houses, hotel]
    color_group: str
    landing_frequency: float = 0.0
    houses: int = 0
    owner: Optional['Player'] = None

@dataclass
class Player:
    name: str
    money: int
    properties: List[Property]
    position: int = 0
    
    def can_afford(self, amount: int) -> bool:
        return self.money >= amount
    
    def pay(self, amount: int) -> bool:
        if self.can_afford(amount):
            self.money -= amount
            return True
        return False
    
    def receive(self, amount: int):
        self.money += amount
    
    def get_properties_in_color_group(self, color_group: str) -> List[Property]:
        return [p for p in self.properties if p.color_group == color_group]
    
    def owns_complete_set(self, color_group: str) -> bool:
        color_group_sizes = {
            "brown": 2,
            "light_blue": 3,
            "pink": 3,
            "orange": 3,
            "red": 3,
            "yellow": 3,
            "green": 3,
            "dark_blue": 2
        }
        owned = len(self.get_properties_in_color_group(color_group))
        return owned == color_group_sizes.get(color_group.lower(), 0)
    
    def calculate_net_worth(self) -> int:
        property_value = sum(p.price + (p.houses * (p.price // 2)) for p in self.properties)
        return self.money + property_value
    
    
def property_to_dict(prop):
    return {
        'name': prop.name,
        'position': prop.position,
        'price': prop.price,
        'rent': prop.rent,
        'color_group': prop.color_group,
        'landing_frequency': prop.landing_frequency,
        'houses': prop.houses,
        'owner': prop.owner.name if prop.owner else None
    }

def player_to_dict(player):
    return {
        'name': player.name,
        'money': player.money,
        'position': player.position,
        'properties': [property_to_dict(prop) for prop in player.properties]
    }