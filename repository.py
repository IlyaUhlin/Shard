import json
from asyncio import Lock

from WORLD.models.entity import Entity
from WORLD.models.serializers.entity_serializer import EntitySerializer


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

class Storage(Repository):
    def init(self):
        self.path = "world.json"
    async def get_map(self):
        data = await self.read()
        return data["map"]

    async def get_entity(self, entity_id: int):
        data = await self.read()
        entity_data = data["entities"].get(entity_id)
        if entity_data:
            return EntitySerializer.from_dict(entity_data)
        return None

    async def save_entity(self, entity: Entity, entity_id: int):
        data = await self.read()
        data["entities"][entity_id] = EntitySerializer.to_dict(entity)
