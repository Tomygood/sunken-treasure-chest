import curses
import time
from enum import Enum, auto
from unittest import case

from ..core.level import import_map_from_index
from ..core.utils_types import Pos
from ..core.splash_text import get_random_splash_text
from ..core.consts import MAPS_PATH, X_MAX, Y_MAX

from .cli_logging import clear_log
from .cli_display import *
from .cli_colors import init_colors
from ..core.game_instance import Game_instance, GAME_PHASE
from .level_editor import run_level_editor


class GAME_STATES(Enum):
    MENU = auto()
    LEVEL_SELECTION = auto()
    RUNNING = auto()
    GAME_OVER = auto()

# Define the target FPS
TARGET_FPS = 30
GAME_UPDATE_INTERVAL = 4  # Update game logic every 8 frames
FRAME_TIME = 1.0 / TARGET_FPS  # Time per frame in seconds


def main(stdscr: curses.window) -> None:
    """Main function to run the CLI application."""
    clear_log()

    init_curses(stdscr)
    init_colors()
    stdscr.clear()

    
    end = False
    last_time = time.time()
    selection_index = int()
    area_displays = list()
    cursor = Pos(0, 0)
    selected_building = None
    level = None
    game_instance = None
    game_state = GAME_STATES.MENU
    splash = get_random_splash_text()
    selection = False
    
    time_active = 0

    max_y, max_x = stdscr.getmaxyx()

    while not end:
        current_time = time.time()
        elapsed_time = current_time - last_time

        key = stdscr.getch()

        # Exit on 'q' key press
        if key == ord('q'):
            end = True
        
        # Update and render at fixed FPS
        if elapsed_time >= FRAME_TIME or elapsed_time < 0:
            time_active += 1
            last_time = current_time

            stdscr.erase()


            # Check terminal size
            if max_y < SCREEN_HEIGHT or max_x < SCREEN_WIDTH:
                stdscr.addstr(0, 0, TERMINAL_TOO_SMALL_TEXT)
                continue
        
            
            match game_state:
                case GAME_STATES.MENU:
                   # Input handling
                    
                    if key == ord('\n'): 
                        selection_index = 0
                        level = import_map_from_index(MAPS_PATH, selection_index)
                        game_state = GAME_STATES.LEVEL_SELECTION
                    
                    elif key == ord('e'):
                        # Exit curses temporarily to run level editor
                        terminate_curses(stdscr)
                        run_level_editor(MAPS_PATH)
                        init_curses(stdscr)
                        init_colors()

                    # Rendering
                    
                    render_menu(stdscr, splash)

                case GAME_STATES.LEVEL_SELECTION:

                    flag = False
                    
                    # Input handling

                    if key == curses.KEY_RIGHT:
                        selection_index += 1
                        flag = True
                    elif key == curses.KEY_LEFT:
                        selection_index -= 1
                        flag = True

                    if flag:
                        level = import_map_from_index("./data/maps", selection_index)

                    if key == ord('\n'):
                        game_instance = Game_instance(level)
                        cursor = Pos(0, 0)
                        game_state = GAME_STATES.RUNNING

                    # Rendering

                    display_level_select(stdscr, level)



                case GAME_STATES.RUNNING:
                    if time_active % (GAME_UPDATE_INTERVAL) == 0:
                        activated_traps = game_instance.update()
                        for trap in activated_traps:
                            area_displays.append([trap.pos, trap.get_range_of_effect(), 10])

                    if time_active % (TARGET_FPS) == 0 and game_instance.state != GAME_PHASE.FIGHT_PHASE:
                        game_instance.time_until_next_wave -= 1

                    if key == ord('a') and game_instance.state != GAME_PHASE.FIGHT_PHASE:
                        game_instance.time_until_next_wave -= 1
                        if game_instance.time_until_next_wave < 0:
                            game_instance.time_until_next_wave = 0

                    if game_instance.finished:
                        game_state = GAME_STATES.GAME_OVER

                    display_game_instance(game_instance, stdscr)
                    display_area_effects(stdscr, area_displays, game_instance)

                    if not selection:
                        if key == curses.KEY_UP and cursor.x > 0:
                            cursor = cursor + Pos(-1, 0)
                        elif key == curses.KEY_DOWN and cursor.x < X_MAX-1:
                            cursor = cursor + Pos(1, 0)
                        elif key == curses.KEY_LEFT and cursor.y > 0:
                            cursor = cursor + Pos(0, -1)
                        elif key == curses.KEY_RIGHT and cursor.y < Y_MAX-1:  
                            cursor = cursor + Pos(0, 1)

                        selected_building, open_menu = display_selection_info(stdscr, cursor, game_instance)
                        
                        if key == ord('\n') and open_menu:
                            selection = True

                            
                    else:
                        # Upgrade menu
                        if selected_building is not None:
                            display_upgrade_menu(stdscr, cursor, game_instance, selected_building)


                            if key == ord('\n') and selected_building.is_upgradable():
                                cost = selected_building.get_upgrade_cost()
                                if game_instance.gold >= cost:
                                    selected_building.upgrade()
                                    selection = False

                            elif key == ord('d'):
                                game_instance.buildings.remove(selected_building)
                                selection = False
                        
                        # Building creation menu
                        else:
                            placeable_buildings = game_instance.get_placeable_buildings(cursor)


                            if key == curses.KEY_RIGHT:
                                selection_index += 1
                            elif key == curses.KEY_LEFT:
                                selection_index -= 1

                            display_building_menu(stdscr, cursor, game_instance, placeable_buildings, selection_index)
                                
                            if key == ord('\n'):
                                building_to_place = placeable_buildings[selection_index % len(placeable_buildings)]
                                if game_instance.gold >= building_to_place.get_construction_cost():
                                    game_instance.place(building_to_place, cursor)
                                    selection = False


                        if key == ord('c'):
                            selection = False
            
                case GAME_STATES.GAME_OVER:
                    display_game_instance(game_instance, stdscr)
                    display_area_effects(stdscr, area_displays, game_instance)
                    display_game_over(stdscr, game_instance)
                    

                    if key == ord('\n'):
                        game_state = GAME_STATES.MENU
                        splash = get_random_splash_text()
                        
            
            stdscr.refresh()
        else:
            # Sleep for the remaining frame time
            time.sleep(FRAME_TIME - elapsed_time)
    
    terminate_curses(stdscr)
