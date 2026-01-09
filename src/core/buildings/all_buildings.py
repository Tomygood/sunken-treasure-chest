from .all_traps import *
from .all_towers import *
from ..utils_types import Pos

bp = Pos(-1, -1)
ALL_BUILDINGS = [ExplosiveTrap(bp), ArcherTower(bp), ElectricTower(bp), Pitfall(bp), PlaceableWall(bp)]