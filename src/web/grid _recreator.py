from ..core.tiles import *
from ..core.utils_types import Pos

def num_to_tile(num):
    lookup = {
        "void": 0, # VOID
        "wall": 3, # WALL
        "floor": 2, # FLOOR
        "building": 1, # BUILDING
        "treasure": 4, # TREASURE
        "entrance": 5  # ENTRANCE
    }
    tile_index = lookup.get(num, 0)
    return ALL_TILES[tile_index]
def index_to_grid(ind):
    return [[num_to_tile(i) for i in j]for j in ind]