from WORLD.models.entity import Entity


class Creature(Entity):
    def __init__(self):
        super().__init__()
        self._energy = 0

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value: int):
        self._energy = max(0, value)
