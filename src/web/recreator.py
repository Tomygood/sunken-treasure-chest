from ..core.buildings.building import Building
from ..core.buildings.all_towers import *
from ..core.buildings.all_traps import *
from ..core.buildings.tower import Tower
from ..core.buildings.trap import Trap
from ..core.tiles import *
from ..core.utils_types import Pos
from ..core.all_entities import *
from ..core.entity import Entity, STRATS
from ..core.utils_types import Pos
from ..core.splash_text import get_random_splash_text
from ..core.game_instance import *
from ..core.tiles import TILES_TYPES
from ..core.treasure import Jewel

from ..core.utils_types import Pos


def dict_to_instance(d):
    res = Game_instance(Level_template("0b01", None, None, None, None))
    res.buildings = [dict_to_building(x) for x in d["buildings"]]
    res.current_wave = d["current_wave"]
    res.finished = d["finished"]
    res.gold = d["gold"]
    res.grid = [[num_to_tile(x) for x in y] for y in d["grid"]]
    res.template.entrance = Pos(d["entrance"][0], d["entrance"][1])
    res.heros = [dict_to_entity(x) for x in d["heros"]]

    heros_left = []
    for (ennemy, nb) in d["heros_left_to_spawn"]:
        heros_left.append((dict_to_constr_ent(ennemy), nb))

    res.heros_left_to_spawn = heros_left

    res.monsters = [dict_to_entity(x) for x in d["monsters"]]
    res.score = d["score"]
    res.state = GAME_PHASE.BUILDING_PHASE if d["state"] == 0 else GAME_PHASE.FIGHT_PHASE
    res.time_until_next_wave = d["time_until_next_wave"]
    res.treasure.jewels = [dict_to_jewel(x, res.heros) for x in d["treasure"]]
    res.treasure.pos = Pos(d["t_pos"][0], d["t_pos"][1])
    res.wave_clock = d["wave_clock"]
    res.won = d["won"]
    w_res = []
    for w in d["waves"]:
        d_res = {}
        for X in w:
            d_res[dict_to_constr_ent(X[0])] = X[1]
        w_res.append(d_res)
    res.template.waves = w_res
    return res


def dict_to_building(dict) -> Building:
    building_pos = Pos(dict["position"][0], dict["position"][1])

    if dict["name"] == "Archer Tower":
        new_tower = ArcherTower(building_pos)
        new_tower.hp = dict["hp"]
        new_tower.maxhp = dict["maxhp"]

    elif dict["name"] == "Explosive Trap":
        new_tower = ExplosiveTrap(building_pos)
        new_tower.number_of_activations = dict["activation"]
    
    elif dict["name"] == "Pitfall":
        new_tower = Pitfall(building_pos)
        new_tower.number_of_activations = dict["activation"]

    elif dict["name"] == "Electric Tower":
        new_tower = ElectricTower(building_pos)
        new_tower.hp = dict["hp"]
        new_tower.maxhp = dict["maxhp"]

    elif dict["name"] == "Placeable Wall":
        new_tower = PlaceableWall(building_pos)
        new_tower.hp = dict["hp"]
        new_tower.maxhp = dict["maxhp"]

    else:
        raise Exception(
            "Batiment non existant. \n Il n'a peut-être pas été ajouté à web/recreator.py :3")

    new_tower.level = dict["level"]
    new_tower.dead = dict["dead"]

    return new_tower


def dict_to_constr_ent(d) -> Entity:
    """
    Returns the constructor entity of a dictonary

    :param d: Dictionnary of the constructor
    :return: Constructor of the entity
    :rtype: Entity
    """
    if d["name"] == "Rat":
        return Rat
    if d["name"] == "Paladin":
        return Paladin
    if d["name"] == "Seal":
        return Seal
    if d["name"] == "Eel":
        return Eel
    if d["name"] == "Clod":
        return Clod
    if d["name"] == "Fih":
        return Fih
    if d["name"] == "Turtle":
        return Turtle
    if d["name"] == "Liar":
        return Liar


def dict_to_entity(dict) -> Entity:
    if dict["name"] == "Rat":
        new_entity = Rat()
    elif dict["name"] == "Paladin":
        new_entity = Paladin()
    elif dict["name"] == "Seal":
        new_entity = Seal()
    elif dict["name"] == "Eel":
        new_entity = Eel()
    elif dict["name"] == "Clod":
        new_entity = Clod()
    elif dict["name"] == "Fih":
        new_entity = Fih()
    elif dict["name"] == "Turtle":
        new_entity = Turtle()
    elif dict["name"] == "Liar":
        new_entity = Liar()
    else:
        raise Exception(
            f"Entitée non existante: {dict['name']}. \n Il n'a peut-être pas été ajouté à web/recreator.py >:3")

    new_entity.dead = dict["dead"]
    new_entity.position = Pos(dict["position"][0], dict["position"][1])
    new_entity.is_ally = dict["ally"]
    new_entity.maxhp = dict["maxhp"]
    new_entity.hp = dict["hp"]
    new_entity.strength = dict["strength"]
    new_entity.speed = dict["speed"]
    new_entity.clock = dict["clock"]
    new_entity.has_jewel = dict["has_jewel"]
    new_entity.home = Pos(dict["home"][0], dict["home"][1])
    new_entity.set_ai(num_to_ai(dict["ai"]))

    return new_entity


def num_to_ai(n: int) -> STRATS:
    match n:
        case 0:
            return STRATS.RUNNER
        case 1:
            return STRATS.SMARTER
        case 2:
            return STRATS.ATTACK


def dict_to_jewel(dict, entity_list: list[Entity]) -> Jewel:
    jewel_pose = Pos(dict["position"][0], dict["position"][1])
    new_jewel = Jewel(jewel_pose)
    new_jewel.carried = dict["carried"]
    new_jewel.present = dict["present"]
    if new_jewel.carried:
        for entity in entity_list:
            if entity.position == jewel_pose:
                new_jewel.carrier = entity
    return new_jewel


def num_to_tile(num):
    lookup = {
        "void": 0,  # VOID
        "wall": 3,  # WALL
        "floor": 2,  # FLOOR
        "building": 1,  # BUILDING
        "treasure": 4,  # TREASURE
        "entrance": 5  # ENTRANCE
    }
    tile_index = lookup.get(num, 0)
    return ALL_TILES[tile_index]


def index_to_grid(ind):
    return [[num_to_tile(i) for i in j]for j in ind]
