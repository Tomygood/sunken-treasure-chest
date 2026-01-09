from .tiles import Tile, ALL_TILES
from .entity import Entity
from .all_entities import ALL_ENTITIES
from os import listdir
from os.path import isfile, join
from .utils_types import Pos


class Level_template():
    def __init__(self, name: str, grid: list[list[Tile]], waves: list[dict[Entity, int]], entrance_pos, tres_pos: Pos):
        self.name = name
        self.grid = grid
        self.waves = waves
        self.treasure = tres_pos
        self.entrance = entrance_pos


def import_map(filename):
    f = open(filename, "r").read().split("\n\n")
    grid = f[1]
    x = [list(lis) for lis in grid.split("\n")]
    res = []
    entrance_pos = Pos(-1, -1)
    tres_pos = Pos(-1, -1)
    i = 0
    j = 0
    for li in x:
        j = 0
        res_tmp = []
        for c in li:
            if c == 'T':
                tres_pos = Pos(i, j)
            if c == 'E':
                entrance_pos = Pos(i, j)
            for t in ALL_TILES:
                if c == t.ascii:
                    res_tmp.append(t)
                    break
            j += 1
        i += 1
        res.append(res_tmp)

    waves = f[2].split("\n")[:-1]
    res_wave = []
    for w in waves:
        res_wave_tmp = {}
        monsts = w.split(",")
        for m in monsts:
            tmp = m.split("-")
            monst_ascii = tmp[0]
            num_monst = tmp[1]
            for M in ALL_ENTITIES:
                if M.ascii == monst_ascii:
                    res_wave_tmp[M] = int(num_monst)
                    break
        res_wave.append(res_wave_tmp)
        
    return Level_template(f[0], res, res_wave, entrance_pos, tres_pos)


def import_map_from_index(mypath: str, index: int) -> Level_template:
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles.sort()

    if len(onlyfiles) == 0:
        raise Exception("No map files found in the specified directory.")

    map_file = onlyfiles[index % len(onlyfiles)]

    level = import_map(join(mypath, map_file))
    return level
