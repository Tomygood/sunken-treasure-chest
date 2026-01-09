from typing import Any,Dict, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from os import listdir
from os.path import isfile, join
from .web.to_dict import to_dict, only_change, tiles_types_to_num
from .web.recreator import  dict_to_instance
from .core.level import import_map, import_map_from_index
from .core.game_instance import Game_instance, GAME_PHASE
from .core.utils_types import Pos
from .core.buildings.all_buildings import ALL_BUILDINGS
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



NB_GENS = 20

def prepare_json(g: Game_instance):
    res = {"base": to_dict(g)}
    change = []
    
    for _ in range(NB_GENS):
        g.update()
        if g.state == GAME_PHASE.BUILDING_PHASE:
            change.append(only_change(g))
            res["changes"] = change
            return res 
        change.append(only_change(g))
        if g.finished:
            break
    res["changes"] = change
    return res


@app.post("/game-update")
def get_update(Game:Dict[Any,Any]):
    return prepare_json(dict_to_instance(Game))


@app.get("/get-startup-game/{id}")
def get_start_game(id: int):
    return to_dict(Game_instance(import_map_from_index("data/maps", id)))


@app.get("/get-map-info/{id}")
def get_map_info(id: int):
    d = to_dict(Game_instance(import_map_from_index("data/maps", id)))
    return {"grid": d["grid"], "nb_waves": len(d["waves"])}


@app.get("/list-maps")
def list_maps():
    maps_dir = "data/maps"
    files = [f for f in listdir(maps_dir) if isfile(join(maps_dir, f))]
    files.sort()
    result: List[Dict[str, Any]] = []
    for idx, fname in enumerate(files):
        lvl = import_map(join(maps_dir, fname))
        grid = [[tiles_types_to_num(tile.type) for tile in row] for row in lvl.grid]
        result.append({
            "id": idx,
            "name": lvl.name,
            "grid": grid,
            "nb_waves": len(lvl.waves)
        })
    return result



#{game:gameInstance,x:<x>,y:<y>}
@app.post("/get_building_placable")
def tt(G:Dict[Any,Any]):
    g:Game_instance = dict_to_instance(G["game"])

    tile_info = g.get_tile_info(Pos(G["x"],G["y"]))
    tile = tile_info["tile"]
    
    if "building" in tile_info:
        # Upgrade or delete
        building = tile_info["building"]
        return (building, building.get_long_desc())


    # New building
    poss = g.get_placeable_buildings(Pos(G["x"],G["y"]))


    return [(x, x.get_long_desc()) for x in poss]

@app.post("/place_building")
def placer(G: Dict[Any, Any]):
    # Expects a dict with: {"game": <state>, "building": <name>, "x": int, "y": int}
    g: Game_instance = dict_to_instance(G.get("game"))
    building_name = G.get("building")
    x = G.get("y")
    y = G.get("x")

    if building_name is None or x is None or y is None:
        return to_dict(g)

    chosen = None
    for b in ALL_BUILDINGS:
        if b.name == building_name:
            chosen = b
            break

    if chosen is not None:
        try:
            g.place(chosen, Pos(x, y))
        except Exception:
            pass

    return to_dict(g)


@app.post("/upgrade_building")
def upgrade_building(G: Dict[Any, Any]):
    # Expects a dict with: {"game": <state>, "x": int, "y": int}
    g: Game_instance = dict_to_instance(G.get("game"))
    x = G.get("y")
    y = G.get("x")

    if x is None or y is None:
        return to_dict(g)

    tile_info = g.get_tile_info(Pos(x, y))
    if "building" in tile_info:
        building = tile_info["building"]
        try:
            g.upgrade(building)
        except Exception as e:
            print(f"Failed to upgrade: {e}")

    return to_dict(g)


@app.post("/delete_building")
def delete_building(G: Dict[Any, Any]):
    # Expects a dict with: {"game": <state>, "x": int, "y": int}
    g: Game_instance = dict_to_instance(G.get("game"))
    x = G.get("y")
    y = G.get("x")

    if x is None or y is None:
        return to_dict(g)

    tile_info = g.get_tile_info(Pos(x, y))
    if "building" in tile_info:
        building = tile_info["building"]
        try:
            g.buildings.remove(building)
            g.gold += building.get_construction_cost() // 2
        except Exception as e:
            print(f"Failed to delete: {e}")

    return to_dict(g)


app.mount("/", StaticFiles(directory="src/web/static", html=True), name="static")
