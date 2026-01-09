from enum import Enum, auto
import random
from .level import Level_template
from .utils_types import TasMin
from .buildings.building import Building
from .treasure import Treasure
from .utils_types import Pos
from .buildings.all_buildings import ALL_BUILDINGS
from .entity import Entity, STRATS
from .tiles import TILES_TYPES
from .pathfinding import Astar
from .consts import *
from .buildings.trap import Trap
from ..cli.cli_logging import log_message
from .buildings.tower import Tower
import random


class GAME_PHASE(Enum):
    BUILDING_PHASE = auto()
    FIGHT_PHASE = auto()


class Game_instance():
    def __init__(self, template: Level_template):
        self.template = template
        self.gold = BASE_GOLD
        self.grid = None
        if template.grid is not None:
            self.grid = [[x for x in y] for y in template.grid]
        self.monsters: list[Entity] = []
        self.heros: list[Entity] = []
        self.buildings: list[Building] = []
        self.state = GAME_PHASE.BUILDING_PHASE

        self.time_until_next_wave = BUILDING_TIME
        self.current_wave = 0

        self.score = 0

        self.wave_clock = 0
        self.heros_left_to_spawn = list()

        self.finished = False
        self.won = False
        self.treasure = Treasure(template.treasure)

    def can_place(self, building: Building, pos: Pos) -> bool:
        placable = True

        if "building" in building.building_restriction:
            for nbuilding in self.buildings:
                if nbuilding.pos == pos:
                    placable = False
                    break

        tile = self.grid[pos.x][pos.y]
        if tile.type in building.building_restriction:
            placable = False

        if tile.type == TILES_TYPES.TREASURE or tile.type == TILES_TYPES.ENTRANCE:
            placable = False

        return placable

    def place(self, building: Building, pos: Pos):
        if self.can_place(building, pos):
            nbuilding = building.place_to(pos)
            self.buildings.append(nbuilding)
            nbuilding.pos = pos
            self.gold -= building.get_construction_cost()
            self.score += building.get_construction_cost()

    def upgrade(self, building: Building):
        if building.is_upgradable():
            if building.get_upgrade_cost() <= self.gold:
                self.gold -= building.get_upgrade_cost()
                building.upgrade()
                # Mise à jour du score pour bonifier l'upgrade
                self.score += int(building.cost[building.level]
                                  * building.level * 0.75)

    def get_tile_info(self, pos: Pos) -> dict:

        info = {}

        for monsters in self.monsters:
            if monsters.pos == pos:
                info["monster"] = monsters

        for buildings in self.buildings:
            if buildings.pos == pos:
                info["building"] = buildings

        for hero in self.heros:
            if hero.position == pos:
                info["hero"] = hero

        info["tile"] = self.grid[pos.x][pos.y]

        return info

    def get_jewels_left(self) -> int:
        return self.treasure.jewels_left

    def get_placeable_buildings(self, pos: Pos) -> list[str]:
        res = list()

        for building in ALL_BUILDINGS:
            if self.can_place(building, pos):
                res.append(building)

        return res

    def move_entity(self, ent: Entity, p: Pos):
        if self.grid[p.x][p.y].walkable:
            for m in self.monsters:
                if m.position == p:
                    ent.attack(m)
                    return

            for h in self.heros:
                if h.position == p:
                    ent.attack(h)
                    return
            for b in self.buildings:
                if isinstance(b, Tower):
                    if b.pos == p:
                        ent.attack(b)
                        return

            ent.position = p

    def get_path_ent(self, ent: Entity):
        blocked = []
        all_tow: list[Tower] = [
            x.pos for x in self.buildings if isinstance(x, Tower)]

        blocked += all_tow
        if ent.get_ai() == STRATS.SMARTER:
            blocked += [x.pos for x in self.buildings if isinstance(x, Trap)]
        if ent.is_ally:
            blocked += [x.position for x in self.monsters]
        else:
            blocked += [x.position for x in self.heros]
        if ent.is_ally:
            min_p = ent.position
            min_d = 9999
            for j in self.heros:
                if min_d < ent.position.dist(j.pos):
                    min_p = j.pos
                    min_d = ent.position.dist(j.pos)
            return Astar(self.grid, ent.position, min_p, blocked=blocked)
        else:
            if ent.has_jewel:
                return Astar(self.grid, ent.position, ent.home, blocked=blocked)
            if (len(all_tow) != 0) and (ent.get_ai() == STRATS.ATTACK or self.treasure.jewels_left == 0):
                min_p = ent.position
                min_d = 9999
                for t in all_tow:
                    if min_d > ent.position.dist(t):
                        min_p = t
                        min_d = ent.position.dist(t)
                return Astar(self.grid, ent.position, min_p, blocked=blocked)

            else:
                min_p = self.treasure.pos
                min_d = 9999
                for j in self.treasure.jewels:
                    if j.present and not j.carried:
                        if min_d > ent.position.dist(j.pos):
                            min_p = j.pos
                            min_d = ent.position.dist(j.pos)

                return Astar(self.grid, ent.position,
                             min_p, blocked=blocked)
        return None

    def update_entity(self, ent: Entity):
        p = self.get_path_ent(ent)
        if p is None:
            return
        if len(p) <= 1:
            return None
        
        if ent.clock == 0:
            ent.clock = ent.get_speed()
            self.move_entity(ent, p[1])

            for j in self.treasure.jewels:
                if not j.carried:
                    if j.pos == ent.position:
                        j.take(ent)
                        break
        else:
            ent.clock -= 1

    def begin_wave(self):
        wave_info = self.template.waves[self.current_wave]
        self.heros_left_to_spawn = list(wave_info.items())
        self.current_wave += 1

    def add_hero(self, hero: Entity):
        proba = random.randint(1, 100)
        if proba < 20:
            hero.set_ai(STRATS.ATTACK)
        if proba > 80:
            hero.set_ai(STRATS.SMARTER)
        hero.position = self.template.entrance
        self.heros.append(hero)
        hero.home = self.template.entrance

    def update_building(self, building: Building) -> bool:
        return building.attack(self.heros)

    def update(self) -> list[Building]:
        activated_buildings = list()

        match self.state:
            case GAME_PHASE.BUILDING_PHASE:
                if self.time_until_next_wave <= 0:
                    self.state = GAME_PHASE.FIGHT_PHASE
                    self.time_until_next_wave = 0
                    self.begin_wave()

            case GAME_PHASE.FIGHT_PHASE:

                if len(self.heros) == 0 and not self.heros_left_to_spawn:
                    if self.current_wave == len(self.template.waves):
                        self.finished = True
                        self.won = True
                        return activated_buildings
                    else:
                        self.state = GAME_PHASE.BUILDING_PHASE
                        self.time_until_next_wave = BUILDING_TIME
                        self.gold += MONEY_PER_WAVE

                if self.treasure.game_lost():
                    self.finished = True
                    self.won = False
                    return activated_buildings

                # Hero spawning
                if self.heros_left_to_spawn:
                    if self.wave_clock <= 0:
                        # Choose a random hero to spawn
                        random_index = random.randint(0, len(self.heros_left_to_spawn) - 1)
                        entity_class, num_entity = self.heros_left_to_spawn[random_index]
                        self.add_hero(entity_class())
                        num_entity -= 1
                        if num_entity <= 0:
                            self.heros_left_to_spawn.pop(random_index)
                        else:
                            self.heros_left_to_spawn[random_index] = (entity_class,
                                                           num_entity)
                        self.wave_clock = WAVE_CLOCK
                    else:
                        self.wave_clock -= 1

                deads = []
                for h in self.heros:
                    if h.dead:
                        deads.append(h)
                        continue
                    self.update_obj(h)
                    if h.dead:
                        deads.append(h)
                for h in deads:
                    if h.has_jewel:
                        for j in self.treasure.jewels:
                            if j.carried and j.carrier == h:
                                j.drop()
                    self.heros.remove(h)

                deads = []

                for b in self.buildings:
                    if self.update_obj(b):
                        activated_buildings.append(b)
                    if b.dead:
                        deads.append(b)
                for b in deads:
                    self.buildings.remove(b)

                self.treasure.update()
        return activated_buildings

    def update_obj(self, x) -> bool | None:
        if isinstance(x, Entity):
            self.update_entity(x)
        if isinstance(x, Building):
            return self.update_building(x)
