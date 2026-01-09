import unittest
from core.consts import X_MAX, Y_MAX, MAX_MAP_NAME_LEN
from core.level import import_map


MAPS_PATH = "data/maps"

class TestMaps(unittest.TestCase):
    def test_map_dimensions(self):
        from src.core.level import import_map_from_index
        import os

        map_files = [f for f in os.listdir(MAPS_PATH) if os.path.isfile(os.path.join(MAPS_PATH, f))]
        for index in range(len(map_files)):

            path = os.path.join(MAPS_PATH, map_files[index])
            
            # Validate map formatting
            f = open(path, "r").read().split("\n\n")
            if len(f) != 3:
                self.fail(f"Map file {map_files[index]} is improperly formatted.")

            level = import_map(path)

            # Validate map name length
            self.assertGreater(len(level.name), 0, f"Map file {map_files[index]} has an empty name.")
            self.assertLessEqual(len(level.name), MAX_MAP_NAME_LEN, f"Map file {map_files[index]} has a name longer than {MAX_MAP_NAME_LEN} characters.")

            # Validate grid dimensions
            self.assertEqual(len(level.grid), X_MAX, f"Map file {map_files[index]} has incorrect number of rows.")
            for row in level.grid:
                self.assertEqual(len(row), Y_MAX, f"Map file {map_files[index]} has incorrect number of columns in a row.")

            # Check if entrance and treasure positions are within bounds
            self.assertTrue(0 <= level.entrance.x < X_MAX and 0 <= level.entrance.y < Y_MAX, f"Map file {map_files[index]} has entrance out of bounds.")
            self.assertTrue(0 <= level.treasure.x < X_MAX and 0 <= level.treasure.y < Y_MAX, f"Map file {map_files[index]} has treasure out of bounds.")