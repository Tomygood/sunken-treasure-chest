from enum import Enum, auto


class TILES_TYPES(Enum):
    VOID = auto()
    BASIC_WALL = auto()
    BASIC_FLOOR = auto()
    BASIC_BUILDING = auto()
    TREASURE = auto()
    ENTRANCE = auto()


class Tile():
    def __init__(self, type: TILES_TYPES, walkable: bool, build: bool, ascii: str):
        self.type = type
        self.walkable = walkable
        self.buildable = build
        self.ascii = ascii

    def __repr__(self):
        return str(self.type)


ALL_TILES = [
    Tile(TILES_TYPES.VOID, False, False, " "),
    Tile(TILES_TYPES.BASIC_BUILDING, True, True, "O"),
    Tile(TILES_TYPES.BASIC_FLOOR, True, False, "."),
    Tile(TILES_TYPES.BASIC_WALL, False, False, "#"),
    Tile(TILES_TYPES.TREASURE, True, False,"T"),
    Tile(TILES_TYPES.ENTRANCE, True, False,"E")
]

MAP_TILE_LOOKUP = {
    TILES_TYPES.VOID: ALL_TILES[0],
    TILES_TYPES.BASIC_BUILDING: ALL_TILES[1],
    TILES_TYPES.BASIC_FLOOR: ALL_TILES[2],
    TILES_TYPES.BASIC_WALL: ALL_TILES[3],
    TILES_TYPES.TREASURE: ALL_TILES[4],
    TILES_TYPES.ENTRANCE: ALL_TILES[5]
}
