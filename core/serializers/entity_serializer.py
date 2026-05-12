from entities.creature import Creature
from entities.wall import Wall
from entities.energy_source import EnergySource

class EntitySerializer:
    @staticmethod
    def to_dict(entity) -> dict:
        data = {
            'type': entity.__class__.__name__,
            'id': entity.id,
            'x': entity.x,
            'y': entity.y
        }

        if hasattr(entity, 'energy'):
            data['energy'] = entity.energy

        if hasattr(entity, 'amount'):
            data['amount'] = entity.amount

        return data

    @staticmethod
    def from_dict(data: dict):
        type_map = {
            'Creature': Creature,
            'Wall': Wall,
            'EnergySource': EnergySource
        }

        cls = type_map[data['type']]
        entity = cls()
        entity._id = data['id']
        entity.x = data['x']
        entity.y = data['y']

        if 'energy' in data:
            entity.energy = data['energy']

        if 'amount' in data:
            entity.amount = data['amount']

        return entity