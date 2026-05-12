from entities.entity import Entity


class EnergySource(Entity):
    def __init__(self):
        super().__init__()
        self._amount = 0

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value: int):
        self._amount = max(0, value)