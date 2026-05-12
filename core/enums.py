from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class ContractType(Enum):
    MOVE = "move"
    LOOK = "look"
    ABSORB = "absorb"
    DEPLETED = "depleted"