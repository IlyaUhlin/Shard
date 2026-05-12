import json
import random
from typing import List, Dict, Any

from core.map import Map
from core.dispatcher import Dispatcher
from core.TransactionPool import TransactionPool, Contract
from core.enums import Direction
from entities.creature import Creature
from entities.energy_source import EnergySource
from entities.wall import Wall
from repository import Storage


class GameLoop:
    def __init__(self, width: int = 20, height: int = 20, 
                 num_creatures: int = 5, num_energy_sources: int = 10):
        self.map = Map(width, height)
        self.dispatcher = Dispatcher(self.map)
        self.storage = Storage("world.json")
        self.tick = 0
        self.running = False
        
        self._initialize_world(num_creatures, num_energy_sources)

    def _initialize_world(self, num_creatures: int, num_energy_sources: int):
        for _ in range(num_creatures):
            creature = Creature()
            creature.energy = 20
            self._place_entity_randomly(creature)

        for _ in range(num_energy_sources):
            source = EnergySource()
            source.amount = random.randint(30, 100)
            self._place_entity_randomly(source)

    def _place_entity_randomly(self, entity):
        placed = False
        attempts = 0
        max_attempts = 100
        
        while not placed and attempts < max_attempts:
            x = random.randint(0, self.map.width - 1)
            y = random.randint(0, self.map.height - 1)
            placed = self.map.add_entity(entity, x, y)
            attempts += 1
        
        if not placed:
            raise RuntimeError(f"Failed to place entity {entity.id} after {max_attempts} attempts")

    def start(self):
        self.running = True
        print(f"Game started! Tick: {self.tick}")
        print(f"Creatures: {len(self.map.get_creatures())}, Energy sources: {len(self.map.get_energy_sources())}")

    def stop(self):
        self.running = False
        print(f"Game stopped at tick {self.tick}")

    def run_tick(self) -> Dict[str, Any]:
        if not self.running:
            return {"error": "Game not running"}

        self.tick += 1
        stats = {
            "tick": self.tick,
            "actions": [],
            "creatures_count": len(self.map.get_creatures()),
            "energy_sources_count": len(self.map.get_energy_sources())
        }

        creatures = self.map.get_creatures()
        
        for creature in creatures:
            if creature.energy <= 0:
                TransactionPool.create(creature.id, creature.id, Contract.depleted())
                continue

            action = self._decide_action(creature)
            
            if action["type"] == "move":
                TransactionPool.create(creature.id, creature.id, Contract.move(action["direction"]))
                stats["actions"].append({"entity": creature.id, "action": "move", "direction": action["direction"].value})
            
            elif action["type"] == "look":
                TransactionPool.create(creature.id, creature.id, Contract.look())
                stats["actions"].append({"entity": creature.id, "action": "look"})
            
            elif action["type"] == "absorb":
                TransactionPool.create(creature.id, creature.id, Contract.absorb())
                stats["actions"].append({"entity": creature.id, "action": "absorb"})

        self.dispatcher.dispatch_all_pending()

        for creature in self.map.get_creatures():
            if creature.energy <= 0:
                TransactionPool.create(creature.id, creature.id, Contract.depleted())
        
        self.dispatcher.dispatch_all_pending()

        stats["creatures_count"] = len(self.map.get_creatures())
        stats["energy_sources_count"] = len(self.map.get_energy_sources())

        return stats

    def _decide_action(self, creature: Creature) -> Dict[str, Any]:
        if creature.energy < 5:
            neighbors = self.map.get_neighbors(creature.x, creature.y)
            energy_sources = [n for n in neighbors if isinstance(n, EnergySource)]
            if energy_sources:
                return {"type": "absorb"}

        directions = list(Direction)
        return {"type": "move", "direction": random.choice(directions)}

    def run(self, max_ticks: int = 100):
        self.start()
        
        try:
            while self.running and self.tick < max_ticks:
                stats = self.run_tick()
                
                if stats.get("creatures_count", 0) == 0:
                    print(f"All creatures died at tick {self.tick}")
                    break
                
                if self.tick % 10 == 0:
                    print(f"Tick {stats['tick']}: Creatures={stats['creatures_count']}, "
                          f"Energy sources={stats['energy_sources_count']}")
        finally:
            self.stop()

    def save(self, filename: str = "world.json"):
        data = {
            "tick": self.tick,
            "map": self.map.to_dict(),
            "entities": {}
        }
        
        for entity in self.map.get_all_entities():
            from core.serializers.entity_serializer import EntitySerializer
            data["entities"][entity.id] = EntitySerializer.to_dict(entity)
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"World saved to {filename}")

    def load(self, filename: str = "world.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            
            self.tick = data.get("tick", 0)
            self.map = Map(data["map"]["width"], data["map"]["height"])
            self.dispatcher = Dispatcher(self.map)
            
            from core.serializers.entity_serializer import EntitySerializer
            
            for entity_data in data["entities"].values():
                entity = EntitySerializer.from_dict(entity_data)
                self.map.add_entity(entity, entity.x, entity.y)
            
            print(f"World loaded from {filename} (tick {self.tick})")
            return True
        except Exception as e:
            print(f"Failed to load world: {e}")
            return False