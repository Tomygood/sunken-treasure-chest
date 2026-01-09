from ..utils_types import Pos
from ..entity import Entity
from .building_descriptions import *
from ..tiles import TILES_TYPES


class Building():
    def __init__(self, p: Pos, c: list[int], b: list[TILES_TYPES], n: str):
        self.pos = p
        self.cost = c
        self.building_restriction = b
        self.level = 1
        self.name = n
        self.dead = False

    def get_range_of_effect(self) -> int:
        """
        returns the the area of the building effect, 0 if single target
        
        :return: range of the effect
        :rtype: int
        """
        pass

    def damage(self, e: Entity):
        """
        inflict damage to an entity
        
        :param e: the entity which is recieving the damage
        :type e: Entity
        """
        
    def place_to(self, p: Pos):
        """
        Create a clone of the original building and place it at the pos entered in parameters
        Then returns the created Building

        :param p: Description
        :type p: Pos
        :return: the cloned Building
        :rtype: Building
        """
        pass

    def attack(self, enemies: list[Entity]) -> bool:
        """
        Attacks nearby entities and inflicts them damage

        :param enemies: The list of all enemies in the map
        :type enemies: list[Entity]

        :return: whether an attack was made
        :rtype: bool
        """
        
    def upgrade(self):
        self.level += 1

    def is_upgradable(self) -> bool:
        return self.level < len(self.cost)
    
    def get_construction_cost(self) -> int:
        return self.cost[0]
    
    def get_upgrade_cost(self) -> int:
        if self.is_upgradable:
            return self.cost[self.level]
        else: 
            return 0
        
    def get_short_desc(self) -> str:
        if self.name not in short_dic:
            return "-w-"
        return short_dic[self.name]
    
    def get_long_desc(self) -> str:
        if self.name not in long_dic:
            return ">:3 \n OwO"
        return long_dic[self.name]
