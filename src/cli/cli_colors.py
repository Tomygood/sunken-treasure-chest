import curses
from ..core.tiles import TILES_TYPES


# Define color pairs
DEFAULT_COLOR = 0
CURSOR_INVALID_COLOR = 1
CURSOR_UPGRADE_COLOR = 3
CURSOR_VALID_COLOR = 2
RED_TEXT_COLOR = 4

ENEMY_COLOR = 5


WALL_COLOR = 6
FLOOR_COLOR = 7
BUILDABLE_FLOOR_COLOR = 8
TREASURE_COLOR = 9
ENTRANCE_COLOR = 10
EXPLOSION_COLOR = 11


TYPE_TO_COLOR = {
    TILES_TYPES.BASIC_WALL: WALL_COLOR,
    TILES_TYPES.BASIC_FLOOR: FLOOR_COLOR,
    TILES_TYPES.BASIC_BUILDING: BUILDABLE_FLOOR_COLOR,
    TILES_TYPES.TREASURE: TREASURE_COLOR,
    TILES_TYPES.ENTRANCE: ENTRANCE_COLOR,
    TILES_TYPES.VOID: DEFAULT_COLOR
}

def init_colors() -> None:
    """Initialize color pairs for curses."""

    if not curses.has_colors():
        raise Exception("Terminal does not support colors.")

    curses.start_color()
    
    curses.init_pair(CURSOR_VALID_COLOR, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(CURSOR_UPGRADE_COLOR, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(CURSOR_INVALID_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(RED_TEXT_COLOR, curses.COLOR_RED, curses.COLOR_BLACK)

    curses.init_pair(ENEMY_COLOR, curses.COLOR_YELLOW, curses.COLOR_MAGENTA)


    curses.init_pair(WALL_COLOR, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(FLOOR_COLOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(BUILDABLE_FLOOR_COLOR, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(TREASURE_COLOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(ENTRANCE_COLOR, curses.COLOR_BLACK, curses.COLOR_RED)

    curses.init_pair(EXPLOSION_COLOR, curses.COLOR_YELLOW, curses.COLOR_RED)