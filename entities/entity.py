class Entity:
    _id_counter = 0

    def __init__(self):
        Entity._id_counter += 1
        self._id = Entity._id_counter
        self._x = -1
        self._y = -1
        self._position = (self._x, self._y)

    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value
        self._position = (self._x, self._y)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value
        self._position = (self._x, self._y)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position: tuple[int, int]):
        self._position = position
        self._x = position[0]
        self._y = position[1]