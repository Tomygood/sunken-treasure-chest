from .tower import Tower
from ..entity import Entity
from ..tiles import TILES_TYPES
from ..tiles import TILES_TYPES

class ArcherTower(Tower):
    def __init__(self, p):
        cost = [100, 100, 200, 300, 500]
        building_restriction = [TILES_TYPES.BASIC_WALL, TILES_TYPES.BASIC_FLOOR, TILES_TYPES.VOID]
        name = "Archer Tower"
        base_range = 4
        hp = 500
        super().__init__(p, cost, building_restriction, name, base_range, hp)

    def get_range(self) -> int:
        return self.base_range + self.level - 1
    
    def get_range_of_effect(self) -> int:
        return 0
    
    def damage(self, e: Entity):
        inflicted_damage = 5 + (self.level - 1) * 8
        e.take_damage(inflicted_damage)

    def upgrade(self):
        self.hp += 150
        self.maxhp += 150
        super().upgrade()
    
    def get_hp(self) -> int:
        return self.hp 
    
    def get_maxhp(self) -> int:
        return self.maxhp
    
    def place_to(self, p) -> Tower:
        cloned = ArcherTower(p)
        return cloned
    
    def attack(self, enemies) -> bool:
        in_range : list[Entity] = []
        center = self.pos

        for enemy in enemies:
            if enemy.position.dist(center) <= self.get_range():
                in_range.append(enemy)

        if len(in_range) > 0:
            lowest_life_enemy = in_range[0]
            for enemy in in_range:
                if enemy.hp < lowest_life_enemy.hp:
                    lowest_life_enemy = enemy

            self.damage(lowest_life_enemy)
            return True
        
        return False
    

class ElectricTower(Tower):
    def __init__(self, p):
        cost = [300, 300, 500]
        building_restriction = [TILES_TYPES.BASIC_WALL, TILES_TYPES.BASIC_FLOOR, TILES_TYPES.VOID]
        name = "Electric Tower"
        base_range = 4
        hp = 450
        super().__init__(p, cost, building_restriction, name, base_range, hp)

    def get_range(self) -> int:
        return self.base_range
    
    def get_range_of_effect(self) -> int:
        return 1 + self.level
    
    def damage(self, e: Entity):
        inflicted_damage = 5 + (8 * self.level)
        e.take_damage(inflicted_damage)

    def upgrade(self):
        self.hp += 75
        self.maxhp += 75
        super().upgrade()
    
    def get_hp(self) -> int:
        return self.hp 
    
    def get_maxhp(self) -> int:
        return self.maxhp
    
    def place_to(self, p) -> Tower:
        cloned = ElectricTower(p)
        return cloned
    
    def attack(self, enemies) -> bool:
        center = self.pos

        has_attacked = False
        attacked_enemies = 0 

        
        for enemy in enemies:
            if enemy.position.dist(center) <= self.get_range():
                self.damage(enemy)
                has_attacked = True
                attacked_enemies += 1

                if attacked_enemies == self.get_range_of_effect():
                    return True

        return has_attacked
    

class PlaceableWall(Tower):
    def __init__(self, p):
        cost = [50, 50, 100]
        building_restriction = [TILES_TYPES.BASIC_BUILDING, TILES_TYPES.VOID, TILES_TYPES.BASIC_WALL]
        name = "Placeable Wall"
        base_range = 0
        hp = 400
        super().__init__(p, cost, building_restriction, name, base_range, hp)

    def get_range(self) -> int:
        return self.base_range
    
    def get_range_of_effect(self) -> int:
        return 0
    
    def damage(self, e: Entity):
        inflicted_damage = 0 
        e.take_damage(inflicted_damage)

    def upgrade(self):
        self.maxhp += 200 
        self.hp = self.maxhp
        super().upgrade()
    
    def get_hp(self) -> int:
        return self.hp 
    
    def get_maxhp(self) -> int:
        return self.maxhp
    
    def place_to(self, p) -> Tower:
        cloned = PlaceableWall(p)
        return cloned
    
    def attack(self, enemies) -> bool:
        return False