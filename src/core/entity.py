from enum import Enum, auto
from .utils_types import Pos


class STRATS(Enum):
    RUNNER = auto()
    SMARTER = auto()
    ATTACK = auto()


class Entity():

    ascii = " "

    def __init__(self, p: Pos, ally: bool, maxhp: int, strength: int, name: str, speed: int):
        self.name = name
        self.dead = False
        self.position = p
        self.is_ally = ally
        self.maxhp = maxhp
        self.hp = maxhp
        self.strength = strength
        self.has_jewel = False
        self.home = p
        self.speed = speed
        self.clock = speed
        self.ai = STRATS.RUNNER

    def action(self):
        pass

    def attack(self, other):
        other.take_damage(self.strength)

    def set_ai(self, ai: STRATS):
        self.ai = ai

    def get_ai(self):
        return self.ai

    def take_damage(self, n: int):
        self.hp -= n
        if self.hp <= 0:
            self.dead = True
            
    def get_hp(self):
        return self.hp
    
    def get_max_hp(self):
        return self.maxhp

    def get_speed(self) -> int:
        return self.speed
    
    def __lt__(self, other):
        return self.clock < other.clock

    def __gt__(self, other):
        return self.clock > other.clock
