
from ..core.buildings.building import Building
from ..core.buildings.all_towers import *
from ..core.buildings.all_traps import *
from ..core.buildings.tower import Tower
from ..core.buildings.trap import Trap
from ..core.game_instance import Game_instance, GAME_PHASE
from ..core.entity import STRATS


def to_dict(game: Game_instance):
    gold = game.gold
    score = game.score
    if game.state == GAME_PHASE.BUILDING_PHASE:
        phase = 0
    else:
        phase = 1
    monsters = [entity_to_dict(m) for m in game.monsters]
    heros = [entity_to_dict(h) for h in game.heros]
    building = [building_to_dict(b) for b in game.buildings]
    treasure = [jewel_to_dict(j) for j in game.treasure.jewels]
    grid = [[tiles_types_to_num(x.type) for x in y] for y in game.grid]
    heros_left_to_spawn = [(temp_entity_to_dict(x), y)
                           for (x, y) in game.heros_left_to_spawn]
    wave_res = []
    for wave_i in game.template.waves:
        wave_i_tab = []
        for (enn, nb) in wave_i.items():
            wave_i_tab.append((temp_entity_to_dict(enn), nb))
        wave_res.append(wave_i_tab)

    return {
        "gold": gold,
        "score": score,
        "state": phase,
        "monsters": monsters,
        "heros": heros,
        "buildings": building,
        "treasure": treasure,
        "grid": grid,
        "time_until_next_wave": game.time_until_next_wave,
        "wave_clock": game.wave_clock,
        "heros_left_to_spawn": heros_left_to_spawn,
        "finished": game.finished,
        "won": game.won,
        "waves": wave_res,
        "current_wave": game.current_wave,
        "entrance": (game.template.entrance.x, game.template.entrance.y),
        "t_pos": (game.treasure.pos.x, game.treasure.pos.y)
    }


def only_change(game: Game_instance):
    monsters = [entity_to_dict(m) for m in game.monsters]
    heros = [entity_to_dict(h) for h in game.heros]
    treasure = [jewel_to_dict(j) for j in game.treasure.jewels]
    heros_left_to_spawn = [(temp_entity_to_dict(x), y)
                           for (x, y) in game.heros_left_to_spawn]
    building = [building_to_dict(b) for b in game.buildings]
    return {
        "gold": game.gold,
        "monsters": monsters,
        "heros": heros,
        "monsters": monsters,
        "buildings": building,
        "treasure": treasure,
        "heros_left_to_spawn": heros_left_to_spawn,
        "score": game.score,
        "state":  0 if game.state == GAME_PHASE.BUILDING_PHASE else 1,
        "finished": game.finished,
        "won": game.won,
        "current_wave": game.current_wave,
        "time_until_next_wave": game.time_until_next_wave
    }


def temp_entity_to_dict(ent):
    # Handle both entity instances and entity classes
    name = ent.name if hasattr(ent, 'name') else (ent.__name__ if isinstance(ent, type) else str(ent))
    return {
        "name": name
    }


def entity_to_dict(entity):
    return {
        "name": entity.name,
        "dead": entity.dead,
        "position": (entity.position.x, entity.position.y),
        "ally": entity.is_ally,
        "maxhp": entity.maxhp,
        "hp": entity.hp,
        "speed": entity.get_speed(),
        "clock": entity.clock,
        "strength": entity.strength,
        "has_jewel": entity.has_jewel,
        "home": (entity.home.x, entity.home.y),
        "ai": ai_to_num(entity.get_ai())

    }


def ai_to_num(ai: STRATS):
    match ai:
        case STRATS.RUNNER:
            return 0
        case STRATS.SMARTER:
            return 1
        case STRATS.ATTACK:
            return 2


def building_to_dict(building):
    if isinstance(building, Tower):
        return {
            "name": building.name,
            "position": (building.pos.x, building.pos.y),
            "level": building.level,
            "dead": building.dead,
            "hp": building.hp,
            "maxhp": building.maxhp,
        }
    else:
        return {
            "name": building.name,
            "position": (building.pos.x, building.pos.y),
            "level": building.level,
            "dead": building.dead,
            "activation": building.number_of_activations
        }


def jewel_to_dict(jewel):
    return {
        "position": (jewel.pos.x, jewel.pos.y),
        "carried": jewel.carried,
        "present": jewel.present
    }


def tiles_types_to_num(tile):
    if tile == TILES_TYPES.VOID:
        return "void"
    if tile == TILES_TYPES.BASIC_WALL:
        return "wall"
    if tile == TILES_TYPES.BASIC_FLOOR:
        return "floor"
    if tile == TILES_TYPES.BASIC_BUILDING:
        return "building"
    if tile == TILES_TYPES.TREASURE:
        return "treasure"
    if tile == TILES_TYPES.ENTRANCE:
        return "entrance"
