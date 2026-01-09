from .tiles import Tile
from .utils_types import Pos
from queue import PriorityQueue


def weight(t: Tile, p: Pos, blocked: list[Pos] = None) -> int:
    if p in blocked:
        return 50
    return 1


def h(p1: Pos, p2: Pos):
    return max(abs(p1.x - p2.x), abs(p1.y-p2.y))


def path(prevs: dict[Pos, Pos], end: Pos, beg: Pos):
    res = [end]
    while res[-1] != beg:
        new = prevs[res[-1]]
        res.append(new)
    res.reverse()
    return res


DIRS = [
    Pos(-1, -1),
    Pos(-1, 0),
    Pos(-1, 1),
    Pos(0, -1),
    Pos(0, 1),
    Pos(1, -1),
    Pos(1, 0),
    Pos(1, 1)
]


def Astar(grid: list[list[Tile]], start: Pos, end: Pos, weight_fun=None, blocked: list[Pos] = None) -> list[Pos]:
    pq = PriorityQueue()
    if weight_fun is None:
        weight_fun = weight
    seen = {}
    prevs: dict[Pos, Pos] = {}
    dists: dict[Pos, int] = {}
    dists[start] = 0
    pq.put((h(start, end), start))
    while not pq.empty():
        node = pq.get()[1]
        if node in seen:
            continue
        if node == end:
            return path(prevs, node, start)
        seen[node] = True
        for d in DIRS:
            new = node+d
            if new.x < 0 or new.x >= len(grid):
                continue
            if new.y < 0 or new.y >= len(grid[0]):
                continue
            tile = grid[new.x][new.y]
            if not tile.walkable:
                continue
            if new not in seen:
                if new not in dists:
                    dists[new] = dists[node] + weight_fun(tile, new, blocked)
                    prevs[new] = node
                else:
                    if dists[node] + weight_fun(tile, new, blocked) < dists[new]:
                        prevs[new] = node
                        dists[new] = dists[node] + \
                            weight_fun(tile, new, blocked)
                pq.put((dists[new] + h(new, end), new))
    return None
