import curses
import time
from enum import Enum, auto
from ..core.utils_types import Pos
from ..core.tiles import Tile, TILES_TYPES, MAP_TILE_LOOKUP
from ..core.all_entities import ALL_ENTITIES
from .cli_display import GAME_ORIGIN, display_tile, display_char, SCREEN_WIDTH
from .cli_colors import init_colors, CURSOR_VALID_COLOR
from .main import init_curses
from .cli_logging import log_message
from ..core.consts import X_MAX, Y_MAX, MAX_MAP_NAME_LEN
from ..core.level import Level_template, import_map
import os
from os import listdir
from os.path import isfile, join

# Frame rate control
TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS


class EDITOR_STATES(Enum):
    MAIN_MENU = auto()
    DUNGEON_NAME = auto()
    GRID_EDITING = auto()
    WAVES_EDITING = auto()
    SAVE_MENU = auto()
    LINE_DRAWING = auto()
    LOAD_MENU = auto()


class GRID_MODES(Enum):
    DRAW_WALL = auto()
    DRAW_FLOOR = auto()
    DRAW_BUILDABLE = auto()
    PLACE_ENTRANCE = auto()
    PLACE_TREASURE = auto()
    PLACE_BUILDABLE_SPOT = auto()
    ERASE = auto()


class LevelEditor:
    def __init__(self, maps_path: str):
        self.maps_path = maps_path
        self.grid = [[MAP_TILE_LOOKUP[TILES_TYPES.BASIC_FLOOR] for _ in range(Y_MAX)] for _ in range(X_MAX)]
        self.dungeon_name = "New Dungeon"
        self.entrance_pos = None
        self.treasure_pos = None
        self.waves = []
        self.cursor = Pos(1, 1)
        self.editor_state = EDITOR_STATES.MAIN_MENU
        self.grid_mode = GRID_MODES.DRAW_WALL
        self.line_start = None
        self.line_mode = False
        self.dungeon_name_input = ""
        self.available_maps = []
        self.load_selection_index = 0

    def load_level(self, level: Level_template) -> None:
        """Load a level template into the editor."""
        self.dungeon_name = level.name
        self.grid = [[tile for tile in row] for row in level.grid]
        self.entrance_pos = Pos(level.entrance.x, level.entrance.y) if level.entrance else None
        self.treasure_pos = Pos(level.treasure.x, level.treasure.y) if level.treasure else None
        self.waves = [{entity_class: count for entity_class, count in wave.items()} for wave in level.waves]

    def get_available_maps(self) -> list[str]:
        """Get list of available map files."""
        try:
            return [f for f in listdir(self.maps_path) if isfile(join(self.maps_path, f)) and f.endswith('.map')]
        except:
            return []

    def set_tile(self, pos: Pos, tile: Tile) -> None:

        if not self.is_valid_pos(pos):
            return
        
        if tile.type == TILES_TYPES.ENTRANCE:
            # Remove old entrance if it exists
            if self.entrance_pos and self.entrance_pos != pos:
                log_message("Removing old entrance")
                self.grid[self.entrance_pos.x][self.entrance_pos.y] = MAP_TILE_LOOKUP[TILES_TYPES.BASIC_FLOOR]
            self.entrance_pos = Pos(pos.x, pos.y)
        elif tile.type == TILES_TYPES.TREASURE:
            # Remove old treasure if it exists
            if self.treasure_pos and self.treasure_pos != pos:
                self.grid[self.treasure_pos.x][self.treasure_pos.y] = MAP_TILE_LOOKUP[TILES_TYPES.BASIC_FLOOR]
            self.treasure_pos = Pos(pos.x, pos.y)
        
        self.grid[pos.x][pos.y] = tile

    def is_valid_pos(self, pos: Pos) -> bool:
        """Check if position is within grid bounds."""
        return 0 <= pos.x < X_MAX and 0 <= pos.y < Y_MAX

    def draw_line(self, start: Pos, end: Pos, tile: Tile) -> None:
        """Draw a line of tiles using Bresenham's algorithm."""

        if tile.type == TILES_TYPES.ENTRANCE or tile.type == TILES_TYPES.TREASURE:
            self.set_tile(end, tile)
            return
        
        x0, y0 = start.x, start.y
        x1, y1 = end.x, end.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.set_tile(Pos(x0, y0), tile)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def export_map(self, filename: str) -> None:
        """Export the map to a file."""
        if not self.entrance_pos or not self.treasure_pos:
            return

        # Create directory if it doesn't exist
        os.makedirs(self.maps_path, exist_ok=True)
        filepath = os.path.join(self.maps_path, filename)

        with open(filepath, "w") as f:
            # Header
            f.write(f"{self.dungeon_name}\n\n")

            # Grid
            for row in self.grid:
                for tile in row:
                    f.write(tile.ascii)
                f.write("\n")

            f.write("\n")

            # Waves
            if self.waves:
                for wave in self.waves:
                    wave_str = ""
                    for entity_class, count in wave.items():
                        if wave_str:
                            wave_str += ","
                        wave_str += f"{entity_class.ascii}-{count}"
                    if wave_str:
                        f.write(wave_str + "\n")
            else:
                # Default wave
                f.write("P-1\n")

        log_message(f"Map saved to {filepath}")

    def new_wave(self) -> None:
        """Start a new wave."""
        self.waves.append({})

    def render_main_menu(self, stdscr: curses.window) -> None:
        """Render the main editor menu."""
        menu_items = [
            "═" * 30,
            "  LEVEL EDITOR",
            "═" * 30,
            "",
            "1. Edit Dungeon Name",
            f"   Current: {self.dungeon_name}",
            "",
            "2. Edit Grid",
            f"   Status: {'valid!' if self.entrance_pos and self.treasure_pos else 'invalid'}",
            "",
            "3. Configure Waves",
            f"   Waves configured: {len(self.waves)}",
            "",
            "4. Load Existing Map",
            "5. Save & Exit",
            "6. Exit without Saving",
            "",
            "Q. Back to Main Menu"
        ]

        for i, item in enumerate(menu_items):
            if i < 20:
                try:
                    stdscr.addstr(i + 2, 3, item)
                except:
                    pass

    def render_dungeon_name_menu(self, stdscr: curses.window) -> None:
        """Render the dungeon name input menu."""
        stdscr.addstr(2, 5, "═" * 40)
        stdscr.addstr(3, 5, f"Enter Dungeon Name (max {MAX_MAP_NAME_LEN} chars):")
        stdscr.addstr(4, 5, "─" * 40)
        stdscr.addstr(6, 5, f"Input: {self.dungeon_name_input}")
        stdscr.addstr(8, 5, "Instructions:")
        stdscr.addstr(9, 5, "  - Type to enter name")
        stdscr.addstr(11, 5, "  - Enter to confirm")
        stdscr.addstr(12, 5, "  - Escape to cancel")

    def render_grid_editing(self, stdscr: curses.window) -> None:
        """Render the grid editing screen."""
        # Display grid
        for x in range(X_MAX):
            for y in range(Y_MAX):
                tile = self.grid[x][y]
                display_tile(stdscr, Pos(x, y), tile, origin=GAME_ORIGIN)

        # Display line preview if in line mode
        if self.line_mode and self.line_start:
            self._preview_line(stdscr, self.line_start, self.cursor)

        # Display cursor
        display_tile(stdscr, self.cursor, self.grid[self.cursor.x][self.cursor.y], char="*",origin=GAME_ORIGIN)

        # Display mode info on the right side
        mode_names = {
            GRID_MODES.DRAW_WALL: "W - Draw Walls (#)",
            GRID_MODES.DRAW_FLOOR: "F - Draw Floor (.)",
            GRID_MODES.DRAW_BUILDABLE: "B - Draw Buildable (O)",
            GRID_MODES.PLACE_ENTRANCE: "E - Place Entrance",
            GRID_MODES.PLACE_TREASURE: "T - Place Treasure",
            GRID_MODES.PLACE_BUILDABLE_SPOT: "O - Place Buildable Spot",
            GRID_MODES.ERASE: "X - Erase (Void)",
        }
        
        info_x = Y_MAX + 5 + GAME_ORIGIN.y
        info_start_y = GAME_ORIGIN.x
        try:
            stdscr.addstr(info_start_y, info_x, "═" * 45)
            stdscr.addstr(info_start_y + 1, info_x, f"Mode: {mode_names[self.grid_mode]}")
            stdscr.addstr(info_start_y + 2, info_x, "─" * 45)
            
            if self.line_mode:
                stdscr.addstr(info_start_y + 3, info_x, "*** LINE DRAWING MODE ***")
                stdscr.addstr(info_start_y + 4, info_x, "Move cursor to end position,")
                stdscr.addstr(info_start_y + 5, info_x, "then press Enter to draw line")
                line_offset = 6
            else:
                stdscr.addstr(info_start_y + 3, info_x, "Controls:")
                stdscr.addstr(info_start_y + 4, info_x, "  Arrows: Move cursor")
                stdscr.addstr(info_start_y + 5, info_x, "  Enter: Place tile")
                stdscr.addstr(info_start_y + 6, info_x, "  L: Line drawing mode")
                stdscr.addstr(info_start_y + 7, info_x, "  W/F/B/E/T/O/X: Change mode")
                stdscr.addstr(info_start_y + 8, info_x, "  Q: Return to menu")
                line_offset = 9
            
            status_y = info_start_y + line_offset + 1
            stdscr.addstr(status_y, info_x, "─" * 45)
            stdscr.addstr(status_y + 1, info_x, "Status:")
            stdscr.addstr(status_y + 2, info_x, f"  Cursor: ({self.cursor.x}, {self.cursor.y})")
            stdscr.addstr(status_y + 3, info_x, f"  Entrance: {'✓ Placed' if self.entrance_pos else '✗ Missing'}")
            stdscr.addstr(status_y + 4, info_x, f"  Treasure: {'✓ Placed' if self.treasure_pos else '✗ Missing'}")
            stdscr.addstr(status_y + 6, info_x, f"Dungeon: {self.dungeon_name[:30]}")
        except:
            pass

    def _preview_line(self, stdscr: curses.window, start: Pos, end: Pos) -> None:
        """Preview a line from start to end."""
        x0, y0 = start.x, start.y
        x1, y1 = end.x, end.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        count = 0
        while True:
            if count < 100:
                try:
                    display_tile(stdscr, Pos(x0, y0), self.grid[x0][y0], origin=GAME_ORIGIN, char="+")
                except:
                    pass
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
            count += 1

    def render_waves_editing(self, stdscr: curses.window) -> None:
        """Render the waves editing screen."""
        stdscr.addstr(2, 5, "═" * 50)
        stdscr.addstr(3, 5, "WAVES CONFIGURATION")
        stdscr.addstr(4, 5, "═" * 50)
        stdscr.addstr(6, 5, "Available Enemies:")

        for i, entity_class in enumerate(ALL_ENTITIES):
            try:
                stdscr.addstr(7 + i, 5, f"  {i + 1}. '{entity_class.ascii}' = {entity_class.__name__}")
            except:
                pass

        try:
            info_y = 7 + len(ALL_ENTITIES) + 2
            stdscr.addstr(info_y, 5, "─" * 50)
            stdscr.addstr(info_y + 1, 5, f"Waves Created: {len(self.waves)}")
            stdscr.addstr(info_y + 2, 5, "Commands:")
            stdscr.addstr(info_y + 3, 5, "  N - Create New Wave")
            stdscr.addstr(info_y + 4, 5, "  D - Delete Last Wave")
            stdscr.addstr(info_y + 5, 5, "  1-9 - Add enemy to current wave")
            stdscr.addstr(info_y + 6, 5, "  Q - Return to Menu")
            stdscr.addstr(info_y + 8, 5, "─" * 50)
            stdscr.addstr(info_y + 9, 5, "Current Waves:")

            # Display current waves
            for wave_idx, wave in enumerate(self.waves):
                y = info_y + 10 + wave_idx
                wave_str = f"  Wave {wave_idx + 1}: "
                for entity_class, count in wave.items():
                    wave_str += f"[{entity_class.ascii}x{count}] "
                try:
                    stdscr.addstr(y, 5, wave_str)
                except:
                    pass
        except:
            pass

    def handle_grid_input(self, key: int) -> bool:
        """Handle input during grid editing. Returns True if should exit."""
        if self.line_mode:
            # Movement in line mode
            if key == curses.KEY_UP and self.cursor.x > 0:
                self.cursor.x -= 1
            elif key == curses.KEY_DOWN and self.cursor.x < X_MAX - 1:
                self.cursor.x += 1
            elif key == curses.KEY_LEFT and self.cursor.y > 0:
                self.cursor.y -= 1
            elif key == curses.KEY_RIGHT and self.cursor.y < Y_MAX - 1:
                self.cursor.y += 1
            elif key == ord('\n'):
                # Finish line
                self._apply_grid_mode_line(self.line_start, self.cursor)
                self.line_mode = False
                self.line_start = None
            return False

        # Normal grid editing mode
        # Movement
        if key == curses.KEY_UP and self.cursor.x > 0:
            self.cursor.x -= 1
        elif key == curses.KEY_DOWN and self.cursor.x < X_MAX - 1:
            self.cursor.x += 1
        elif key == curses.KEY_LEFT and self.cursor.y > 0:
            self.cursor.y -= 1
        elif key == curses.KEY_RIGHT and self.cursor.y < Y_MAX - 1:
            self.cursor.y += 1

        # Mode selection
        elif key == ord('w'):
            self.grid_mode = GRID_MODES.DRAW_WALL
        elif key == ord('f'):
            self.grid_mode = GRID_MODES.DRAW_FLOOR
        elif key == ord('b'):
            self.grid_mode = GRID_MODES.DRAW_BUILDABLE
        elif key == ord('e'):
            self.grid_mode = GRID_MODES.PLACE_ENTRANCE
        elif key == ord('t'):
            self.grid_mode = GRID_MODES.PLACE_TREASURE
        elif key == ord('o'):
            self.grid_mode = GRID_MODES.PLACE_BUILDABLE_SPOT
        elif key == ord('x'):
            self.grid_mode = GRID_MODES.ERASE

        # Drawing/Placement
        elif key == ord('\n'):
            self._apply_grid_mode(self.cursor)
        
        elif key == ord('l'):
            # Line drawing mode
            self.line_mode = True
            self.line_start = Pos(self.cursor.x, self.cursor.y)

        elif key == ord('q'):
            return True

        return False

    def _apply_grid_mode(self, pos: Pos) -> None:
        """Apply current grid mode at position."""
        if self.grid_mode == GRID_MODES.DRAW_WALL:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_WALL])
        elif self.grid_mode == GRID_MODES.DRAW_FLOOR:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_FLOOR])
        elif self.grid_mode == GRID_MODES.DRAW_BUILDABLE:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_BUILDING])
        elif self.grid_mode == GRID_MODES.PLACE_ENTRANCE:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.ENTRANCE])
        elif self.grid_mode == GRID_MODES.PLACE_TREASURE:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.TREASURE])
        elif self.grid_mode == GRID_MODES.PLACE_BUILDABLE_SPOT:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_BUILDING])
        elif self.grid_mode == GRID_MODES.ERASE:
            self.set_tile(pos, MAP_TILE_LOOKUP[TILES_TYPES.VOID])

    def _apply_grid_mode_line(self, start: Pos, end: Pos) -> None:
        """Apply current grid mode as a line."""
        if self.grid_mode == GRID_MODES.DRAW_WALL:
            self.draw_line(start, end, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_WALL])
        elif self.grid_mode == GRID_MODES.DRAW_FLOOR:
            self.draw_line(start, end, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_FLOOR])
        elif self.grid_mode == GRID_MODES.DRAW_BUILDABLE:
            self.draw_line(start, end, MAP_TILE_LOOKUP[TILES_TYPES.BASIC_BUILDING])
        elif self.grid_mode == GRID_MODES.ERASE:
            self.draw_line(start, end, MAP_TILE_LOOKUP[TILES_TYPES.VOID])

    def handle_waves_input(self, key: int) -> bool:
        """Handle input during waves editing. Returns True if should exit."""
        if key == ord('n'):
            self.new_wave()
        elif key == ord('d'):
            if self.waves:
                self.waves.pop()
        elif ord('1') <= key <= ord('9'):
            entity_idx = key - ord('1')
            if entity_idx < len(ALL_ENTITIES):
                entity_class = ALL_ENTITIES[entity_idx]
                if not self.waves:
                    self.new_wave()

                if entity_class in self.waves[-1]:
                    self.waves[-1][entity_class] += 1
                else:
                    self.waves[-1][entity_class] = 1
        elif key == ord('q'):
            return True

        return False

    def handle_main_menu_input(self, key: int) -> bool:
        """Handle input in main menu. Returns True if should exit editor."""
        if key == ord('1'):
            self.editor_state = EDITOR_STATES.DUNGEON_NAME
            self.dungeon_name_input = self.dungeon_name
        elif key == ord('2'):
            self.editor_state = EDITOR_STATES.GRID_EDITING
        elif key == ord('3'):
            self.editor_state = EDITOR_STATES.WAVES_EDITING
        elif key == ord('4'):
            self.available_maps = self.get_available_maps()
            self.load_selection_index = 0
            self.editor_state = EDITOR_STATES.LOAD_MENU
        elif key == ord('5'):
            self.editor_state = EDITOR_STATES.SAVE_MENU
        elif key == ord('6'):
            return True
        elif key == ord('q'):
            return True

        return False

    def handle_dungeon_name_input(self, key: int, stdscr: curses.window) -> None:
        """Handle input when editing dungeon name."""
        if key == ord('\n'):
            self.dungeon_name = self.dungeon_name_input
            self.editor_state = EDITOR_STATES.MAIN_MENU
        elif key == 27: # Escape
            self.editor_state = EDITOR_STATES.MAIN_MENU
        elif key == curses.KEY_BACKSPACE:
            if len(self.dungeon_name_input) > 0:
                self.dungeon_name_input = self.dungeon_name_input[:-1]
        elif 32 <= key <= 126 and len(self.dungeon_name_input) < MAX_MAP_NAME_LEN:
            self.dungeon_name_input += chr(key)

    def render_save_menu(self, stdscr: curses.window, filename_input: str) -> None:
        """Render the save menu."""
        stdscr.addstr(2, 5, "═" * 50)
        stdscr.addstr(3, 5, "SAVE DUNGEON")
        stdscr.addstr(4, 5, "═" * 50)
        stdscr.addstr(6, 5, f"Dungeon Name: {self.dungeon_name}")
        stdscr.addstr(7, 5, f"Waves: {len(self.waves)}")
        stdscr.addstr(8, 5, f"Entrance: {'✓' if self.entrance_pos else '✗'}")
        stdscr.addstr(9, 5, f"Treasure: {'✓' if self.treasure_pos else '✗'}")
        
        stdscr.addstr(11, 5, "─" * 50)
        stdscr.addstr(12, 5, "Suggested filename: " + self.dungeon_name.lower().replace(" ", "_") + ".map")
        stdscr.addstr(13, 5, f"Enter filename (without .map): {filename_input}")
        
        stdscr.addstr(15, 5, "Commands:")
        stdscr.addstr(16, 5, "  Enter - Save with entered name (or suggested if empty)")
        stdscr.addstr(17, 5, "  Q - Return to menu without saving")

    def render_load_menu(self, stdscr: curses.window) -> None:
        """Render the load level menu."""
        stdscr.addstr(2, 5, "═" * 50)
        stdscr.addstr(3, 5, "LOAD EXISTING MAP")
        stdscr.addstr(4, 5, "═" * 50)
        
        if not self.available_maps:
            stdscr.addstr(6, 5, "No maps found in the maps directory.")
            stdscr.addstr(8, 5, "Press Q to return to menu.")
        else:
            stdscr.addstr(6, 5, "Available Maps:")
            stdscr.addstr(7, 5, "─" * 50)
            
            for i, map_file in enumerate(self.available_maps):
                prefix = "> " if i == self.load_selection_index else "  "
                try:
                    stdscr.addstr(8 + i, 5, f"{prefix}{i + 1}. {map_file}")
                except:
                    pass
            
            stdscr.addstr(8 + len(self.available_maps) + 1, 5, "─" * 50)
            stdscr.addstr(8 + len(self.available_maps) + 2, 5, "Commands:")
            stdscr.addstr(8 + len(self.available_maps) + 3, 5, "  Up/Down - Navigate")
            stdscr.addstr(8 + len(self.available_maps) + 4, 5, "  Enter - Load selected map")
            stdscr.addstr(8 + len(self.available_maps) + 5, 5, "  Q - Return to menu")

    def handle_load_menu_input(self, key: int) -> bool:
        """Handle input in load menu. Returns True if map was loaded."""
        if not self.available_maps:
            if key == ord('q'):
                self.editor_state = EDITOR_STATES.MAIN_MENU
            return False
        
        if key == curses.KEY_UP and self.load_selection_index > 0:
            self.load_selection_index -= 1
        elif key == curses.KEY_DOWN and self.load_selection_index < len(self.available_maps) - 1:
            self.load_selection_index += 1
        elif key == ord('\n'):
            
            selected_file = self.available_maps[self.load_selection_index]
            filepath = join(self.maps_path, selected_file)
            try:
                level = import_map(filepath)
                self.load_level(level)
                self.editor_state = EDITOR_STATES.MAIN_MENU
                return True
            except Exception as e:
                log_message(f"Failed to load map: {e}")
        elif key == ord('q'):
            self.editor_state = EDITOR_STATES.MAIN_MENU
        
        return False

    def handle_save_menu_input(self, key: int, filename: str) -> tuple:
        """Handle input in save menu. Returns (should_exit, new_filename)."""
        if key == curses.KEY_BACKSPACE:
            return False, filename[:-1]
        elif key == ord('\n'):
            if not filename:
                filename = self.dungeon_name.lower().replace(" ", "_") + ".map"
            if not filename.endswith(".map"):
                filename += ".map"
            self.export_map(filename)
            return True, filename
        elif key == ord('q'):
            self.editor_state = EDITOR_STATES.MAIN_MENU
            return False, ""
        elif 32 <= key <= 126 and len(filename) < SCREEN_WIDTH - 20:
            return False, filename + chr(key)
        
        return False, filename


def run_level_editor(maps_path: str) -> None:
    """Run the level editor in a curses window."""
    def editor_main(stdscr: curses.window):
        init_colors()
        init_curses(stdscr)
        stdscr.clear()
        editor = LevelEditor(maps_path)

        filename_input = ""
        last_time = time.time()

        while True:
            current_time = time.time()
            elapsed_time = current_time - last_time

            # Only render at target FPS
            if elapsed_time >= FRAME_TIME:
                last_time = current_time
                stdscr.erase()

                key = stdscr.getch()

                if key == ord('q') and editor.editor_state == EDITOR_STATES.MAIN_MENU:
                    break

                match editor.editor_state:
                    case EDITOR_STATES.MAIN_MENU:
                        if editor.handle_main_menu_input(key):
                            break
                        editor.render_main_menu(stdscr)

                    case EDITOR_STATES.DUNGEON_NAME:
                        editor.handle_dungeon_name_input(key, stdscr)
                        editor.render_dungeon_name_menu(stdscr)

                    case EDITOR_STATES.GRID_EDITING:
                        if editor.handle_grid_input(key):
                            editor.editor_state = EDITOR_STATES.MAIN_MENU
                        editor.render_grid_editing(stdscr)

                    case EDITOR_STATES.WAVES_EDITING:
                        if editor.handle_waves_input(key):
                            editor.editor_state = EDITOR_STATES.MAIN_MENU
                        editor.render_waves_editing(stdscr)

                    case EDITOR_STATES.LOAD_MENU:
                        editor.handle_load_menu_input(key)
                        editor.render_load_menu(stdscr)

                    case EDITOR_STATES.SAVE_MENU:
                        should_exit, filename_input = editor.handle_save_menu_input(key, filename_input)
                        editor.render_save_menu(stdscr, filename_input)
                        
                        if should_exit:
                            break

                try:
                    stdscr.refresh()
                except:
                    pass
            else:
                time.sleep(0.01)

    curses.wrapper(editor_main)
