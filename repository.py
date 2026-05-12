import json
from asyncio import Lock

from entities.entity import Entity
from core.serializers.entity_serializer import EntitySerializer


class Repository:
    path: str = ""
    lock: Lock = Lock()
    def __init__(self, path: str):
        self.path = path

    async def write(self, data):
        if not data:
            return
        async with self.lock:
            with open(self.path, "w") as file:
                file.write(json.dumps(data, ensure_ascii=False, indent=4))

    async def read(self):
        async with self.lock:
            with open(self.path, "r") as file:
                return json.loads(file.read())

    def write_sync(self, data):
        """Synchronous write for non-async contexts"""
        if not data:
            return
        with open(self.path, "w") as file:
            file.write(json.dumps(data, ensure_ascii=False, indent=4))

    def read_sync(self):
        """Synchronous read for non-async contexts"""
        with open(self.path, "r") as file:
            return json.loads(file.read())

class Storage(Repository):
    def __init__(self, path: str = "world.json"):
        super().__init__(path)
    
    def get_map(self):
        data = self.read_sync()
        return data["map"]

    def get_entity(self, entity_id: int):
        data = self.read_sync()
        entity_data = data["entities"].get(entity_id)
        if entity_data:
            return EntitySerializer.from_dict(entity_data)
        return None

    def save_entity(self, entity: Entity, entity_id: int):
        data = self.read_sync()
        data["entities"][entity_id] = EntitySerializer.to_dict(entity)
        self.write_sync(data)

    def save_world(self, tick: int, map_data: dict, entities_data: dict):
        """Save complete world state"""
        data = {
            "tick": tick,
            "map": map_data,
            "entities": entities_data
        }
        self.write_sync(data)

    def load_world(self):
        """Load complete world state"""
        return self.read_sync()
