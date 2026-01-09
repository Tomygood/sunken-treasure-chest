from .building import Building

class Trap(Building):
    def __init__(self, p, c, b, n, noa: int):
        super().__init__(p, c, b, n)
        self.number_of_activations = noa

    def activate(self):
        self.number_of_activations -= 1
        if self.number_of_activations == 0:
            self.dead = True
