import curses
from typing import Tuple
from ..core.tiles import Tile
from ..core.buildings.building import Building
from ..core.level import Level_template
from ..core.game_instance import Game_instance
from ..core.utils_types import Pos
from ..core.consts import *
from .cli_colors import *
from ..core.entity import Entity
from .cli_logging import log_message
from ..core.buildings.trap import Trap
from ..core.buildings.tower import Tower

# Define constants for display
SCREEN_WIDTH = X_MAX + 100  # Overall screen width
SCREEN_HEIGHT = Y_MAX + 10  # Overall screen height

GAME_ORIGIN = Pos(2, 2)  # Origin point for the game grid display

SELECTION_MENU_HEIGHT = 12  # Height of the selection menu
SELECTION_MENU_ORIGIN = Pos(4, X_MAX + 5) # Origin point for the selection menu

CURSOR_CHAR = "*"  # Character to represent the cursor
TRAPS_CHAR = "."  # Character to represent traps
TOWERS_CHAR = "#"  # Character to represent towers

# String constants
TITLE_TEXT = "DUUUUDE"
START_GAME_TEXT = "Enter to start the game"
SELECT_TEXT = "Press Enter to select this level"
CLOSE_TEXT = "Press 'c' to close"
TERMINAL_TOO_SMALL_TEXT = "Terminal too small"
RESIZE_TERMINAL_HINT = "Make your terminal as big as the frame!"
DELETE_TEXT = "Press 'd' to delete this building"
BUILD_TITLE_TEXT = "* Build *"
EDITOR_TEXT = "Press 'e' to open the level editor"
ADVANCE_WAVE_TEXT = "Hold 'a' to advance"

def display_char(stdscr: curses.window, p: Pos, char: str, color: int = DEFAULT_COLOR, origin: Pos = GAME_ORIGIN) -> None:
    """Display a single character on the screen."""
    try:
        stdscr.addstr(p.x + origin.x, p.y + origin.y, char, curses.color_pair(color))
    except:
        return


def display_tile(stdscr: curses.window, p: Pos, tile: Tile, origin: Pos = GAME_ORIGIN, char: str = ' ', color: int = -1) -> None:
    """Display tile information on the screen."""
    np = p + origin
    if tile is None:
        color = color if color != -1 else TYPE_TO_COLOR[TILES_TYPES.BASIC_FLOOR]
    else:
        color = color if color != -1 else TYPE_TO_COLOR[tile.type]
        if tile.type == TILES_TYPES.TREASURE:
            char = "x"
    try:
        stdscr.addstr(np.x, np.y, char, curses.color_pair(color))
    except:
        return
    
def display_buildings(stdscr: curses.window, buildings: list[Building], game_instance: Game_instance) -> None:
    """Display all buildings on the screen."""
    for b in buildings:
        tile = game_instance.grid[b.pos.x][b.pos.y]
        char = TRAPS_CHAR if isinstance(b, Trap) else TOWERS_CHAR
        display_tile(stdscr, b.pos, tile, origin=GAME_ORIGIN, char=char)


def display_area_effects(stdscr: curses.window, area_displays: list[list], game_instance: Game_instance) -> None:
    """Display area effects on the screen."""
    for area in area_displays:
        center = area[0]
        radius = area[1]
        for x in range(center.x - radius, center.x + radius + 1):
            for y in range(center.y - radius, center.y + radius + 1):
                pos = Pos(x, y)
                if pos.x < 0 or pos.x >= X_MAX or pos.y < 0 or pos.y >= Y_MAX:
                    continue
                if pos.dist(center) <= radius:
                    if game_instance.grid[pos.x][pos.y].type == TILES_TYPES.BASIC_FLOOR:
                        display_tile(stdscr, pos, None, origin=GAME_ORIGIN, color=EXPLOSION_COLOR)
        

        area[2] -= 1

    # Remove expired effects
    area_displays[:] = [area for area in area_displays if area[2] > 0]

def display_game_instance(game_instance: Game_instance, stdscr: curses.window) -> None:
    """Display the entire game instance on the screen."""

    wave_text = f"Wave {game_instance.current_wave}/{len(game_instance.template.waves)}"
    stdscr.addstr(GAME_ORIGIN.x - 1, 2 + (X_MAX - len(wave_text)) // 2, wave_text)
    display_grid(game_instance.grid, stdscr, origin=GAME_ORIGIN)

    display_buildings(stdscr, game_instance.buildings, game_instance)

    display_money(stdscr, game_instance.gold)
    display_heroes(stdscr, game_instance.heros, game_instance)
    display_monsters(stdscr, game_instance.monsters, game_instance)
    display_timer(stdscr, game_instance.time_until_next_wave)
    display_treasure(stdscr, game_instance.treasure)
    display_score(stdscr, game_instance.score)

    # Display list of heroes and their health
    for i, h in enumerate(game_instance.heros):
        if i >= 9:
            break
        hero_text = f"{h.name} {i+1} HP: {h.get_hp()}/{h.get_max_hp()}"
        stdscr.addstr(X_MAX - 9 + i - 1, SCREEN_WIDTH - len(hero_text) - 2, hero_text)

def display_score(stdscr: curses.window, score: int) -> None:
    """Display the player's current score."""
    score_text = f"Score: {score}"
    stdscr.addstr(2, SCREEN_WIDTH - len(score_text) - 2, score_text)

def display_treasure(stdscr: curses.window, treasure) -> None:
    """Display the treasure and its jewels on the screen."""
    for j in treasure.jewels:
        if j.present and not j.carried:
            display_tile(stdscr, j.pos, None, origin=GAME_ORIGIN, char="J", color=TYPE_TO_COLOR[TILES_TYPES.BASIC_FLOOR])
    
    jewels_left = treasure.jewels_left
    display_tile(stdscr, treasure.pos, None, origin=GAME_ORIGIN, char=str(jewels_left), color=TREASURE_COLOR)

def display_heroes(stdscr: curses.window, heroes: list[Entity], game_instance: Game_instance) -> None:
    """Display all heroes on the screen."""
    for i, h in enumerate(heroes):
        tile = game_instance.grid[h.position.x][h.position.y]
        char = "♦" if h.has_jewel else str((i+1)%10)

        display_tile(stdscr, h.position, tile, origin=GAME_ORIGIN, char=char, color=ENEMY_COLOR)




def display_monsters(stdscr: curses.window, monsters: list[Entity], game_instance: Game_instance) -> None:
    """Display all monsters on the screen."""
    for m in monsters:
        tile = game_instance.grid[m.position.x][m.position.y]
        display_tile(stdscr, m.position, tile, origin=GAME_ORIGIN, char=m.ascii)

def display_timer(stdscr: curses.window, time_left: int) -> None:
    """Display the timer for the next wave."""
    if time_left <= 0:
        timer_text = "Wave in progress..."
    else:
        timer_text = f"Next wave in: {time_left}s"

        stdscr.addstr(Y_MAX + 3, 2 + (X_MAX - len(ADVANCE_WAVE_TEXT)) // 2, ADVANCE_WAVE_TEXT)

    stdscr.addstr(Y_MAX + 2, 2 + (X_MAX - len(timer_text)) // 2, timer_text)

def display_grid(grid: list[list[Tile]], stdscr: curses.window, origin: Pos = GAME_ORIGIN) -> None:
    """Display the entire grid of tiles on the screen."""
    for i, row in enumerate(grid):
        for j, tile in enumerate(row):
            display_tile(stdscr, Pos(i, j), tile, origin=origin)


def display_level_select(stdscr: curses.window, level: Level_template) -> None:
    """Display level selection information."""
    origin_x = 2
    origin_y = 8
    origin = Pos(origin_x, origin_y)

    stdscr.addstr((SCREEN_HEIGHT - origin_x) // 2, origin_y - 4, "<")
    stdscr.addstr((SCREEN_HEIGHT - origin_x) // 2, Y_MAX + 4 + origin_y, ">")
    display_grid(level.grid, stdscr, origin=origin)

    wave_text = "Number of waves: " + str(len(level.waves))

    stdscr.addstr(X_MAX + 4, origin_y + (X_MAX - len(wave_text)) // 2, wave_text)
    stdscr.addstr(X_MAX + 6, origin_y + (X_MAX - len(SELECT_TEXT)) // 2, SELECT_TEXT)
    stdscr.addstr(origin_x - 1, origin_y + (X_MAX - len(level.name)) // 2, level.name)

def display_selection_info(stdscr: curses.window, cursor: Pos, game_instance: Game_instance) -> Tuple[Building | None, bool]:
    """Display information about the current selection."""
    info_origin = SELECTION_MENU_ORIGIN

    tile_info = game_instance.get_tile_info(cursor)

    info_text = str()
    open_menu = False
    selected = None
    placeable_buildings = game_instance.get_placeable_buildings(cursor)


    if "monsters" in tile_info or "hero" in tile_info:
        info_text = "Cannot build here!"

    elif not placeable_buildings:
        info_text = "No buildings available to build here!"

    elif "building" in tile_info:
        building = tile_info["building"]
        name_text = f"{building.name} level {building.level}"
        stdscr.addstr(info_origin.x + 2, info_origin.y, name_text)
    
        open_menu = True
        if building.is_upgradable():
            info_text = f"Upgrade cost: {building.get_upgrade_cost()}$"
                
        else:
            info_text = "Max level reached!"
        
        stdscr.addstr(info_origin.x + 4, info_origin.y, info_text)

        additionnal_info = str()
        if isinstance(building, Trap):
            additionnal_info = f"{building.number_of_activations} activations left"
        elif isinstance(building, Tower):
            display_hp_bar(stdscr, info_origin + Pos(6, 0), building.get_hp(), building.get_maxhp(), bar_length=20)

        stdscr.addstr(info_origin.x + 5, info_origin.y, additionnal_info)

        action = "Press enter to modify!"
        stdscr.addstr(info_origin.x + 8, info_origin.y, action)
        selected = building

        return selected, open_menu

    else:
        info_text = "Press enter to build here!"
        for b in placeable_buildings:
            name = b.name
            cost = b.get_construction_cost()
            stdscr.addstr(info_origin.x + 2 + placeable_buildings.index(b), info_origin.y, f"{name} - {cost}$")

        open_menu = True

    display_tile(stdscr, cursor, game_instance.grid[cursor.x][cursor.y], GAME_ORIGIN, CURSOR_CHAR)
    stdscr.addstr(info_origin.x, info_origin.y, info_text)
    return selected, open_menu

def display_hp_bar(stdscr: curses.window, origin: Pos, current_hp: int, max_hp: int, bar_length: int = 20) -> None:
    """Display a health bar at the specified origin."""
    hp_ratio = current_hp / max_hp
    filled_length = int(bar_length * hp_ratio)

    bar = "[" + "#" * filled_length + "-" * (bar_length - filled_length) + "]"
    hp_text = f"HP: {current_hp}/{max_hp}"

    stdscr.addstr(origin.x, origin.y, bar + " " + hp_text)


def display_upgrade_menu(stdscr: curses.window, cursor: Pos, game_instance: Game_instance, tower: Building) -> None:
    """Display the selection menu for upgrading entities."""

    # Upgrade menu content
    if tower.is_upgradable():
        stdscr.addstr(SELECTION_MENU_ORIGIN.x + 2, SELECTION_MENU_ORIGIN.y + 2, f"Upgrade {tower.name} to level {tower.level + 1}")
        stdscr.addstr(SELECTION_MENU_ORIGIN.x + 4, SELECTION_MENU_ORIGIN.y + 2, f"Cost: {tower.get_upgrade_cost()}$")
    else:
        stdscr.addstr(SELECTION_MENU_ORIGIN.x + 4, SELECTION_MENU_ORIGIN.y + 2, "Max level reached!")
    
    stdscr.addstr(SELECTION_MENU_ORIGIN.x + 6, SELECTION_MENU_ORIGIN.y + 2, DELETE_TEXT)
    

    stdscr.addstr(SELECTION_MENU_ORIGIN.x + 1, SELECTION_MENU_ORIGIN.y + (SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2 - len(BUILD_TITLE_TEXT)) // 2, BUILD_TITLE_TEXT)

    display_tile(stdscr, cursor, game_instance.grid[cursor.x][cursor.y], GAME_ORIGIN, CURSOR_CHAR)
    stdscr.addstr(SELECTION_MENU_ORIGIN.x + SELECTION_MENU_HEIGHT - 2, SCREEN_WIDTH - 2 - len(CLOSE_TEXT) - 1, CLOSE_TEXT)

    
    # Selection menu border
    display_borders(stdscr, SELECTION_MENU_ORIGIN, SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2, SELECTION_MENU_HEIGHT)

def display_building_menu(stdscr: curses.window, cursor: Pos, game_instance: Game_instance, placeable_buildings: list[str], index: int) -> None:
    """Display the selection menu for building entities."""

    building = placeable_buildings[index%len(placeable_buildings)]

    # Building menu content
    name = building.name
    desc = building.get_short_desc()
    cost = f"{building.get_construction_cost()}$"

    stdscr.addstr(SELECTION_MENU_ORIGIN.x + 1, SELECTION_MENU_ORIGIN.y + (SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2 - len(BUILD_TITLE_TEXT)) // 2, BUILD_TITLE_TEXT)

    stdscr.addstr(SELECTION_MENU_ORIGIN.x + 3, SELECTION_MENU_ORIGIN.y + (SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2 - len(name)) // 2, name)
    stdscr.addstr(SELECTION_MENU_ORIGIN.x + 4, SELECTION_MENU_ORIGIN.y + (SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2 - len(desc)) // 2, desc)
    
    color = DEFAULT_COLOR
    if game_instance.gold < building.get_construction_cost():
        color = RED_TEXT_COLOR

    stdscr.addstr(SELECTION_MENU_ORIGIN.x + 6, SELECTION_MENU_ORIGIN.y + (SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2 - len(cost)) // 2, cost, curses.color_pair(color))

    arrows = "< >"
    stdscr.addstr(SELECTION_MENU_ORIGIN.x + SELECTION_MENU_HEIGHT - 4, SELECTION_MENU_ORIGIN.y + (SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2 - len(arrows)) // 2, arrows)

    display_tile(stdscr, cursor, game_instance.grid[cursor.x][cursor.y], GAME_ORIGIN, CURSOR_CHAR)
    stdscr.addstr(SELECTION_MENU_ORIGIN.x + SELECTION_MENU_HEIGHT - 2, SCREEN_WIDTH - 2 - len(CLOSE_TEXT) - 1, CLOSE_TEXT)

    # Selection menu border
    display_borders(stdscr, SELECTION_MENU_ORIGIN, SCREEN_WIDTH - SELECTION_MENU_ORIGIN.y - 2, SELECTION_MENU_HEIGHT)

def display_borders(stdscr: curses.window, origin: Pos, width: int, height: int, stars: bool=False) -> None:
    """Display borders around a specified area."""

    char = "* " if stars else "-"
    for x in range(origin.y, origin.y + width):
        stdscr.addstr(origin.x, x, char)
        stdscr.addstr(origin.x + height - 1, x, char)

    char = "* " if stars else "|"
    for y in range(origin.x, origin.x + height):
        stdscr.addstr(y, origin.y, char)
        stdscr.addstr(y, origin.y + width - 1, char)

def display_money(stdscr: curses.window, gold: int) -> None:
    """Display the player's current gold."""
    money_text = f"{gold}$"
    stdscr.addstr(1, SCREEN_WIDTH - len(money_text) - 2, money_text)

def display_game_over(stdscr: curses.window, game_instance: Game_instance) -> None:

    match game_instance.won:
        case True:
            over_text = "YOU WIN! All waves cleared! :)"
        case False:
            over_text = "GAME OVER! All jewels stolen! :("
    
    # Game recap
    jewels_stolen = NB_JEWELS - game_instance.treasure.jewels_left
    recap_text = f"Jewels stolen: {jewels_stolen} | Score: {game_instance.score}"


    stdscr.addstr(SCREEN_HEIGHT // 2 - 2, (SCREEN_WIDTH - len(over_text)) // 2, over_text)
    stdscr.addstr(SCREEN_HEIGHT // 2, (SCREEN_WIDTH - len(recap_text)) // 2, recap_text)

def render_menu(stdscr: curses.window, splash: str) -> None:
    """Render the main menu."""
    # Screen borders
    display_borders(stdscr, Pos(0, 0), SCREEN_WIDTH, SCREEN_HEIGHT)
    
    stdscr.addstr(1, 1, splash)

    stdscr.addstr(SCREEN_HEIGHT // 3, (SCREEN_WIDTH - len(TITLE_TEXT)) // 2, TITLE_TEXT)
    stdscr.addstr(SCREEN_HEIGHT // 2, (SCREEN_WIDTH - len(START_GAME_TEXT)) // 2, START_GAME_TEXT)
    stdscr.addstr(SCREEN_HEIGHT // 2 + 2, (SCREEN_WIDTH - len(EDITOR_TEXT)) // 2, EDITOR_TEXT)

    stdscr.addstr(SCREEN_HEIGHT - 2, SCREEN_WIDTH - len(RESIZE_TERMINAL_HINT) - 2, RESIZE_TERMINAL_HINT)


def init_curses(stdscr) -> curses.window:
    """Initialize the curses application and return the main window."""
    curses.curs_set(0)  # Hide the cursor
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)  # Make getch non-blocking
    return stdscr


def terminate_curses(stdscr: curses.window) -> None:
    """Terminate the curses application and restore terminal settings."""
    stdscr.keypad(False)
    curses.echo()
    curses.nocbreak()
    curses.curs_set(1)  # Show the cursor
    curses.endwin()
