from typing import Dict, List, Optional, Tuple
import random

from core.enums import Direction
from entities.entity import Entity
from entities.creature import Creature
from entities.energy_source import EnergySource
from entities.wall import Wall


class Map:
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self._grid: Dict[Tuple[int, int], Entity] = {}
        self._entities: Dict[int, Entity] = {}

    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_occupied(self, x: int, y: int) -> bool:
        return (x, y) in self._grid

    def get_entity_at(self, x: int, y: int) -> Optional[Entity]:
        return self._grid.get((x, y))

    def get_entity_by_id(self, entity_id: int) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def add_entity(self, entity: Entity, x: int, y: int) -> bool:
        if not self.is_valid_position(x, y):
            return False
        if self.is_occupied(x, y):
            return False
        
        entity.x = x
        entity.y = y
        self._grid[(x, y)] = entity
        self._entities[entity.id] = entity
        return True

    def remove_entity(self, entity_id: int) -> bool:
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        
        pos = (entity.x, entity.y)
        if pos in self._grid:
            del self._grid[pos]
        del self._entities[entity_id]
        return True

    def move_entity(self, entity_id: int, direction: Direction) -> bool:
        entity = self._entities.get(entity_id)
        if not entity:
            return False

        new_x, new_y = entity.x, entity.y
        if direction == Direction.UP:
            new_y -= 1
        elif direction == Direction.DOWN:
            new_y += 1
        elif direction == Direction.LEFT:
            new_x -= 1
        elif direction == Direction.RIGHT:
            new_x += 1

        if not self.is_valid_position(new_x, new_y):
            return False
        if self.is_occupied(new_x, new_y):
            return False

        old_pos = (entity.x, entity.y)
        del self._grid[old_pos]
        
        entity.x = new_x
        entity.y = new_y
        self._grid[(new_x, new_y)] = entity
        return True

    def get_neighbors(self, x: int, y: int) -> List[Entity]:
        neighbors = []
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                entity = self._grid.get((nx, ny))
                if entity:
                    neighbors.append(entity)
        return neighbors

    def get_all_entities(self) -> List[Entity]:
        return list(self._entities.values())

    def get_creatures(self) -> List[Creature]:
        return [e for e in self._entities.values() if isinstance(e, Creature)]

    def get_energy_sources(self) -> List[EnergySource]:
        return [e for e in self._entities.values() if isinstance(e, EnergySource)]

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "entities": {eid: {"type": e.__class__.__name__, "x": e.x, "y": e.y} 
                        for eid, e in self._entities.items()}
        }