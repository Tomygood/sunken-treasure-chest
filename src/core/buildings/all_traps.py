from ..buildings.trap import Trap
from ..entity import Entity
from ..tiles import TILES_TYPES


class ExplosiveTrap(Trap):
    """
    A trap with huge AOE damages but few utilisations
    """
    def __init__(self, p):
        cost = [100, 100, 250]
        building_restriction = [TILES_TYPES.BASIC_WALL, TILES_TYPES.VOID]
        name = "Explosive Trap"
        number_of_activations = 2
        super().__init__(p, cost, building_restriction, name, number_of_activations)

    def get_range_of_effect(self) -> int:
        return 3 + self.level

    def damage(self, e: Entity):
        inflicted_damage = 800 * self.level
        e.take_damage(inflicted_damage)

    def place_to(self, p) -> Trap:
        placed = ExplosiveTrap(p)
        return placed
    
    def attack(self, enemies: list[Entity]) -> bool:
        in_range = []
        center = self.pos
        explose_flag = False

        for enemy in enemies:
            if enemy.position.dist(center) <= self.get_range_of_effect():
                in_range.append(enemy)

                if enemy.position == self.pos:
                    explose_flag = True

        if explose_flag:
            for enemy in in_range:
                self.damage(enemy)
                self.activate()
        
        return explose_flag

class Pitfall(Trap):
    def __init__(self, p):
        cost = [150]
        building_restriction = [TILES_TYPES.BASIC_WALL, TILES_TYPES.VOID]
        name = "Pitfall"
        number_of_activation = 1
        super().__init__(p, cost, building_restriction, name, number_of_activation)

    def get_range_of_effect(self) -> int:
        return 0
    
    def damage(self, e: Entity):
        inflicted_damage = e.get_max_hp()
        e.take_damage(inflicted_damage)

    def place_to(self, p) -> Trap:
        placed = Pitfall(p)
        return placed
    
    def attack(self, enemies: list[Entity]) -> bool:
        center = self.pos
        was_activated = False

        for enemy in enemies:
            if enemy.position == center:
                self.damage(enemy)
                was_activated = True

        if was_activated:
            self.activate()
        return was_activated