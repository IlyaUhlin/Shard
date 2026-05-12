from typing import List, Optional
import random

from core.enums import Direction, ContractType
from core.TransactionPool import TransactionPool, Contract, Transaction
from core.map import Map
from entities.creature import Creature
from entities.energy_source import EnergySource


class Dispatcher:
    def __init__(self, game_map: Map):
        self.map = game_map

    def process_transaction(self, transaction: Transaction) -> bool:
        contract = transaction.contract
        executor = self.map.get_entity_by_id(transaction.executor_id)
        initiator = self.map.get_entity_by_id(transaction.initiator_id)

        if not executor:
            TransactionPool.complete(transaction.id, {"success": False, "error": "Executor not found"})
            return False

        if contract.type == ContractType.MOVE:
            return self._handle_move(transaction, executor)
        elif contract.type == ContractType.LOOK:
            return self._handle_look(transaction, executor)
        elif contract.type == ContractType.ABSORB:
            return self._handle_absorb(transaction, executor)
        elif contract.type == ContractType.DEPLETED:
            return self._handle_depleted(transaction, executor)

        TransactionPool.complete(transaction.id, {"success": False, "error": "Unknown contract type"})
        return False

    def _handle_move(self, transaction: Transaction, creature: Creature) -> bool:
        direction = transaction.contract.direction
        success = self.map.move_entity(creature.id, direction)
        
        if success:
            creature.energy -= 1
            TransactionPool.complete(transaction.id, {"success": True, "action": "move", "direction": direction.value})
        else:
            TransactionPool.complete(transaction.id, {"success": False, "action": "move", "reason": "Invalid move"})
        
        return success

    def _handle_look(self, transaction: Transaction, creature: Creature) -> bool:
        neighbors = self.map.get_neighbors(creature.x, creature.y)
        vision = [
            {
                "id": n.id,
                "type": n.__class__.__name__,
                "x": n.x,
                "y": n.y,
                "energy": getattr(n, 'energy', None),
                "amount": getattr(n, 'amount', None)
            }
            for n in neighbors
        ]
        
        transaction.contract.vision = vision
        creature.energy -= 1
        TransactionPool.complete(transaction.id, {"success": True, "action": "look", "vision": vision})
        return True

    def _handle_absorb(self, transaction: Transaction, creature: Creature) -> bool:
        neighbors = self.map.get_neighbors(creature.x, creature.y)
        energy_sources = [n for n in neighbors if isinstance(n, EnergySource)]

        if not energy_sources:
            TransactionPool.complete(transaction.id, {"success": False, "action": "absorb", "reason": "No energy sources nearby"})
            return False

        source = energy_sources[0]
        absorb_amount = min(10, source.amount)
        
        if absorb_amount <= 0:
            TransactionPool.complete(transaction.id, {"success": False, "action": "absorb", "reason": "Source depleted"})
            return False

        source.amount -= absorb_amount
        creature.energy += absorb_amount
        
        if source.amount <= 0:
            self.map.remove_entity(source.id)

        TransactionPool.complete(transaction.id, {
            "success": True, 
            "action": "absorb", 
            "amount": absorb_amount,
            "creature_energy": creature.energy
        })
        return True

    def _handle_depleted(self, transaction: Transaction, creature: Creature) -> bool:
        if creature.energy <= 0:
            self.map.remove_entity(creature.id)
            TransactionPool.complete(transaction.id, {"success": True, "action": "depleted", "reason": "Creature died"})
            return True
        
        TransactionPool.complete(transaction.id, {"success": False, "action": "depleted", "reason": "Creature still has energy"})
        return False

    def dispatch_all_pending(self) -> int:
        pending = TransactionPool.get_pending_transactions()
        processed = 0
        
        for transaction in pending:
            self.process_transaction(transaction)
            processed += 1
        
        TransactionPool.clear_completed()
        return processed