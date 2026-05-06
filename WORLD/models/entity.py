
class Entity:
    def __init__(self):
        self.energy = 0
        self.x = -1
        self.y = -1

    async def tick(self):
        pass

    def to_dict(self):
        return {
            "energy": self.energy,
            "x": self.x,
            "y": self.y
        }

    @classmethod
    def from_dict(cls, data):
        entity = cls()
        if "energy" in data:
            entity.energy = data["energy"]
        if "x" in data:
            entity.x = data["x"]
            
        entity.energy = data["energy"]