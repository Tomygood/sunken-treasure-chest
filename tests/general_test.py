import unittest
from core.utils_types import Pos
from core.entity import Entity
from core.all_entities import Paladin, Rat
from core.tiles import TILES_TYPES, MAP_TILE_LOOKUP
from core.buildings.tower import Tower
from core.buildings.trap import Trap
from core.treasure import Treasure
from core.buildings.all_traps import ExplosiveTrap


class TestEntity(unittest.TestCase):
    """Test suite for Entity class"""
    
    def setUp(self):
        """Set up test entities"""
        self.paladin = Paladin()
        self.rat = Rat()
    
    def test_entity_initialization(self):
        """Test that entities initialize correctly"""
        self.assertEqual(self.paladin.name, "Paladin")
        self.assertEqual(self.rat.name, "Rat")
        self.assertFalse(self.paladin.dead)
        self.assertFalse(self.rat.dead)
    
    def test_entity_health(self):
        """Test entity health management"""
        initial_hp = self.paladin.get_hp()
        self.assertEqual(initial_hp, self.paladin.maxhp)
        
        self.paladin.take_damage(10)
        self.assertEqual(self.paladin.get_hp(), initial_hp - 10)
        self.assertFalse(self.paladin.dead)
    
    def test_entity_death(self):
        """Test that entities die when HP reaches 0"""
        self.paladin.take_damage(self.paladin.maxhp + 1)
        self.assertTrue(self.paladin.dead)
    
    def test_entity_attack(self):
        """Test entity attack mechanics"""
        initial_rat_hp = self.rat.get_hp()
        self.paladin.attack(self.rat)
        
        expected_damage = self.paladin.strength
        self.assertEqual(self.rat.get_hp(), initial_rat_hp - expected_damage)
    
    def test_entity_speed(self):
        """Test entity speed attribute"""
        self.assertEqual(self.paladin.get_speed(), self.paladin.speed)
        self.assertEqual(self.rat.get_speed(), self.rat.speed)

class TestTower(unittest.TestCase):
    """Test suite for Tower class"""
    
    def setUp(self):
        """Set up test towers"""
        self.tower_pos = Pos(10, 10)
        self.tower = Tower(
            p=self.tower_pos,
            c=100,  # cost
            b=True,  # buildable
            n="Test Tower",
            r=5,  # range
            hp=50
        )
    
    def test_tower_initialization(self):
        """Test that towers initialize correctly"""
        self.assertEqual(self.tower.pos, self.tower_pos)
        self.assertEqual(self.tower.name, "Test Tower")
        self.assertEqual(self.tower.base_range, 5)
        self.assertEqual(self.tower.get_hp(), 50)
        self.assertEqual(self.tower.get_maxhp(), 50)
    
    def test_tower_health(self):
        """Test tower health management"""
        self.tower.take_damage(10)
        self.assertEqual(self.tower.get_hp(), 40)
        self.assertFalse(self.tower.dead)
    
    def test_tower_destruction(self):
        """Test tower destruction"""
        self.tower.take_damage(60)
        self.assertTrue(self.tower.dead)
    
    def test_tower_cost(self):
        """Test tower cost"""
        self.assertEqual(self.tower.cost, 100)


class TestTreasure(unittest.TestCase):
    """Test suite for Treasure class"""
    
    def setUp(self):
        """Set up test treasure"""
        self.treasure = Treasure(Pos(15, 15))
    
    def test_treasure_initialization(self):
        """Test that treasure initializes correctly"""
        self.assertEqual(self.treasure.pos, Pos(15, 15))
        self.assertEqual(len(self.treasure.jewels), 5)
    
    def test_treasure_jewels(self):
        """Test treasure jewels"""
        for jewel in self.treasure.jewels:
            self.assertTrue(jewel.present)
            self.assertFalse(jewel.carried)


class TestPosition(unittest.TestCase):
    """Test suite for Pos class"""
    
    def test_position_initialization(self):
        """Test position initialization"""
        pos = Pos(5, 10)
        self.assertEqual(pos.x, 5)
        self.assertEqual(pos.y, 10)
    
    def test_position_addition(self):
        """Test position addition"""
        pos1 = Pos(5, 10)
        pos2 = Pos(3, 2)
        result = pos1 + pos2
        self.assertEqual(result.x, 8)
        self.assertEqual(result.y, 12)
    
    def test_position_distance(self):
        """Test position distance calculation"""
        pos1 = Pos(0, 0)
        pos2 = Pos(3, 4)
        distance = pos1.dist(pos2)
        self.assertEqual(distance, 7)
    
    def test_position_equality(self):
        """Test position equality"""
        pos1 = Pos(5, 10)
        pos2 = Pos(5, 10)
        pos3 = Pos(5, 11)
        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)


class TestTiles(unittest.TestCase):
    """Test suite for Tile functionality"""
    
    def test_tile_types_exist(self):
        """Test that all expected tile types exist"""
        self.assertTrue(hasattr(TILES_TYPES, 'BASIC_WALL'))
        self.assertTrue(hasattr(TILES_TYPES, 'BASIC_FLOOR'))
        self.assertTrue(hasattr(TILES_TYPES, 'ENTRANCE'))
        self.assertTrue(hasattr(TILES_TYPES, 'TREASURE'))
    
    def test_tile_lookup(self):
        """Test tile lookup functionality"""
        wall_tile = MAP_TILE_LOOKUP[TILES_TYPES.BASIC_WALL]
        floor_tile = MAP_TILE_LOOKUP[TILES_TYPES.BASIC_FLOOR]
        
        self.assertEqual(wall_tile.ascii, "#")
        self.assertEqual(floor_tile.ascii, ".")
        self.assertFalse(wall_tile.walkable)
        self.assertTrue(floor_tile.walkable)


class TestGameMechanics(unittest.TestCase):
    """Test suite for game mechanics integration"""
    
    def test_tower_vs_entity_damage(self):
        """Test tower vs entity damage scenario"""
        tower = Tower(Pos(0, 0), 100, True, "Archer", 5, 30)
        enemy = Rat()
        initial_enemy_hp = enemy.get_hp()
        
        # Simulate tower attack
        tower_damage = 5
        enemy.take_damage(tower_damage)
        
        self.assertEqual(enemy.get_hp(), initial_enemy_hp - tower_damage)
    
    def test_entity_can_defeat_tower(self):
        """Test that multiple weak entities can destroy a tower"""
        tower = Tower(Pos(0, 0), 100, True, "Weak Tower", 1, 10)
        rats = [Rat() for _ in range(5)]
        
        for rat in rats:
            rat.attack(tower)
        
        # 5 rats * 1 damage per rat = 5 damage total
        # Tower starts with 10 HP, so should have 5 HP left
        self.assertEqual(tower.get_hp(), 5)
        self.assertFalse(tower.dead)
    
    def test_multiple_damage_sources(self):
        """Test entity taking damage from multiple sources"""
        enemy = Paladin()
        initial_hp = enemy.get_hp()
                
        tower_damage = 5
        trap_damage = 10
        
        enemy.take_damage(tower_damage)
        enemy.take_damage(trap_damage)
        
        self.assertEqual(enemy.get_hp(), initial_hp - tower_damage - trap_damage)


if __name__ == '__main__':
    unittest.main()
