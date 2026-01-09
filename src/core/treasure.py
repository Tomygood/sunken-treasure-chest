from .utils_types import Pos
from .entity import Entity
from .consts import NB_JEWELS


class Jewel():
    def __init__(self, pos: Pos):
        self.pos = pos
        self.carried = False
        self.carrier: Entity = None
        self.present = True

    def take(self, carrier):
        self.carried = True
        self.carrier = carrier
        self.carrier.has_jewel = True

    def drop(self):
        self.carried = False
        self.carrier.has_jewel = False
        self.carrier = None

    def update(self):
        if self.carried:
            self.pos = self.carrier.position
            if self.pos == self.carrier.home:
                if self.carrier.name == "Liar":
                    self.carrier.has_jewel = False
                else:
                    self.carrier.dead = True
                self.stolen_to_base()

    def stolen_to_base(self):
        self.present = False


class Treasure():
    def __init__(self, pos: Pos):
        self.pos = pos
        self.jewels: list[Jewel] = [Jewel(pos) for _ in range(NB_JEWELS)]
        self.jewels_left = NB_JEWELS

    def update(self):
        for j in self.jewels:
            j.update()

        self.jewels_left = sum(1 for j in self.jewels if j.present and not j.carried)

    def game_lost(self):
        for j in self.jewels:
            if j.present:
                return False
        return True
