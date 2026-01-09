
class Pos():
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, p):
        return Pos(self.x + p.x, self.y + p.y)

    def __eq__(self, value):
        return self.x == value.x and self.y == value.y

    def __ne__(self, value):
        return not self.__eq__(value)

    def __hash__(self):
        return (str(self.x)+","+str(self.y)).__hash__()

    def __lt__(self, other):
        if self.x == other.x:
            return self.y < other.y
        return self.x < other.x

    def __gt__(self, other):
        if self.x == other.x:
            return self.y > other.y
        return self.x > other.x

    def dist(self, p):
        return abs(self.x - p.x) + abs(self.y - p.y)


class TasMin():
    def __init__(self):
        self.tas = []

    def add(self, obj):
        i = len(self.tas)
        self.tas.append(None)
        while True:
            if i == 0:
                self.tas[0] = obj
                break
            new_i = (i-1) // 2
            if self.tas[new_i] > obj:
                self.tas[i] = self.tas[new_i]
                i = new_i
            else:
                self.tas[i] = obj
                break

    def pop(self):
        res = self.tas[0]
        i = 0
        if len(self.tas) == 1:
            self.tas == self.tas[:-1]
            return res
        obj_i = self.tas[len(self.tas)-1]
        self.tas = self.tas[:-1]
        while True:
            fils_droit = (i*2)+2
            fils_gauche = (i*2)+1
            grand_fils = 0
            if fils_gauche >= len(self.tas):
                self.tas[i] = obj_i
                break
            elif fils_droit >= len(self.tas):
                grand_fils = fils_gauche
            else:
                if self.tas[fils_droit] > self.tas[fils_gauche]:
                    grand_fils = fils_droit
                else:
                    grand_fils = fils_gauche
            if obj_i > self.tas[grand_fils]:
                self.tas[i] = self.tas[grand_fils]
                i = grand_fils
                continue
            self.tas[i] = obj_i
            break
        return res
