from .building import Building


class Tower(Building):
    def __init__(self, p, c, b, n, r: int, hp: int):
        super().__init__(p, c, b, n,)
        self.base_range = r
        self.maxhp = hp
        self.hp = hp

    def get_range(self) -> int:
        """
        returns the range of attack of the tower

        :param self: Description
        :return: Description
        :rtype: int
        """
        pass

    def get_hp(self) -> int:
        return self.hp
    
    def get_maxhp(self) -> int:
        return self.maxhp
    
    def take_damage(self, i:int):
        self.hp -= i

        if self.get_hp() <= 0:
            self.dead = True