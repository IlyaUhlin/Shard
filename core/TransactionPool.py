import uuid

from core.enums import Direction, ContractType


class Contract:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def move(cls, direction: Direction):
        return cls(type=ContractType.MOVE, direction=direction)

    @classmethod
    def look(cls):
        return cls(type=ContractType.LOOK, vision=None)

    @classmethod
    def absorb(cls, resource: int = None):
        return cls(type=ContractType.ABSORB, resource=resource)

    @classmethod
    def depleted(cls):
        return cls(type=ContractType.DEPLETED)


class Transaction:
    def __init__(self, initiator_id: int, executor_id: int, contract: Contract):
        self.id = uuid.uuid4().int
        self.initiator_id = initiator_id
        self.executor_id = executor_id
        self.contract = contract

class TransactionPool:
    transactions: dict[int, Transaction] = {}

    @classmethod
    def create(cls, initiator_id: int, executor_id: int, contract: Contract) -> int:
        transaction: Transaction = Transaction(initiator_id, executor_id, contract)
        cls.transactions[transaction.id] = transaction
        return transaction.id

    @classmethod
    def complete(cls, transaction_id: int) -> None:
        transaction: Transaction = cls._get_transaction(transaction_id)
        pass

    @classmethod
    def get_transaction_contract(cls, transaction_id: int) -> Contract | None:
        transaction: Transaction = cls._get_transaction(transaction_id)
        if transaction:
            return transaction.contract
        return None



    @classmethod
    def _get_transaction(cls, id_: int):
        return cls.transactions.get(id_, None)