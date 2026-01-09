from .entity import Entity, STRATS
from .utils_types import Pos
from random import randint


#Classes utilisées pour les tests

class Paladin(Entity):
    ascii = "P"
    name = "Paladin"
    def __init__(self):
        super().__init__(Pos(0, 0), False, 50, 30, self.name, 2)

class Rat(Entity):
    ascii = "r"
    name = "Rat"
    def __init__(self):
        super().__init__(Pos(0, 0), False, 1, 1, self.name, 2)


#Classes réelles

class Eel(Entity):
    ascii = "e"

    def __init__(self):
        p = Pos(0,0)
        ally = False
        maxhp = 800
        strength = 30
        name = "Eel"
        speed = 1
        super().__init__(p, ally, maxhp, strength, name, speed)

    def get_ai(self):
        return STRATS.RUNNER        

class Clod(Entity):
    ascii = "c"

    def __init__(self):
        p = Pos(0,0)
        ally = False
        maxhp = 2000
        strength = 30
        name = "Clod"
        speed = 5
        super().__init__(p, ally, maxhp, strength, name, speed)

    def set_ai(self, ai):
        seed = randint(0,100)
        if seed <= 40:
            self.ai = STRATS.ATTACK
            #clod veut djoufara les tours
            self.strength += 20
        else:
            self.ai = STRATS.SMARTER
            self.maxhp += 500

class Seal(Entity):
    ascii = "s"

    def __init__(self):
        p = Pos(0,0)
        ally = False
        maxhp = 1300
        strength = 30
        name = "Seal"
        speed = 3
        super().__init__(p, ally, maxhp, strength, name, speed)

class Fih(Entity):
    ascii = "f"

    def __init__(self):
        p = Pos(0,0)
        ally = False
        maxhp = 1800
        strength = 40
        name = "Fih"
        speed = 4
        super().__init__(p, ally, maxhp, strength, name, speed)

    def get_ai(self):
        return STRATS.SMARTER


class Turtle(Entity):
    ascii = "t"

    def __init__(self):
        p = Pos(0,0)
        ally = False
        maxhp = 5000
        strength = 25
        name = "Turtle"
        speed = 6
        super().__init__(p, ally, maxhp, strength, name, speed)

class Liar(Entity):
    ascii = "B"

    def __init__(self):
        p = Pos(0,0)
        ally = False
        maxhp = 1500
        strength = 100
        name = "Liar"
        speed = 3 
        super().__init__(p, ally, maxhp, strength, name, speed)

    def take_damage(self, n:int):
        real_damage = n//4
        self.hp -= real_damage

        if self.hp <= 0:
            if self.speed == 2:
                self.dead = True
            else:
                self.speed = 2
                self.hp = self.maxhp


ALL_ENTITIES: list[Entity] = [Paladin,
                             Rat, 
                             Eel, 
                             Clod, 
                             Seal, 
                             Fih,
                             Turtle,
                             Liar]
