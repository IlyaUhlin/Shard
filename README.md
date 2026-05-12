# World Simulation

A Python-based world simulation with creatures, energy sources, and a transaction-based action system.

## Features

- **Creatures**: Autonomous entities that move, look around, and absorb energy
- **Energy Sources**: Resources that creatures can consume to survive
- **Walls**: Obstacles that block movement
- **Transaction System**: Action contracts (move, look, absorb) processed through a dispatcher
- **Save/Load**: Persist world state to JSON files
- **CLI Interface**: Run simulations from command line

## Project Structure

```
/workspace
├── CLI/
│   └── cli.py              # Command-line interface
├── core/
│   ├── TransactionPool.py  # Transaction and contract management
│   ├── dispatcher.py       # Processes transactions
│   ├── enums.py            # Direction and ContractType enums
│   ├── game_loop.py        # Main game loop logic
│   ├── map.py              # World map implementation
│   └── serializers/
│       └── entity_serializer.py  # Entity serialization
├── entities/
│   ├── creature.py         # Creature entity
│   ├── energy_source.py    # Energy source entity
│   ├── entity.py           # Base entity class
│   └── wall.py             # Wall entity
├── STORAGE/
│   └── storage.py          # Storage module (placeholder)
├── repository.py           # Data persistence layer
└── README.md               # This file
```

## Installation

No external dependencies required. Uses Python 3.10+ standard library.

## Usage

### Run a simulation:
```bash
python -m CLI.cli --width 20 --height 20 --creatures 5 --energy-sources 10 --ticks 100
```

### Save world state:
```bash
python -m CLI.cli --creatures 10 --ticks 50 --save my_world.json
```

### Load and continue:
```bash
python -m CLI.cli --load my_world.json --ticks 50
```

### CLI Options:
- `--width`: World width (default: 20)
- `--height`: World height (default: 20)
- `--creatures`: Number of creatures (default: 5)
- `--energy-sources`: Number of energy sources (default: 10)
- `--ticks`: Maximum simulation ticks (default: 100)
- `--save`: Save world to file after simulation
- `--load`: Load world from file before simulation

## Game Mechanics

### Creatures
- Start with 20 energy
- Lose 1 energy per action (move, look)
- Gain energy by absorbing energy sources (up to 10 per absorption)
- Die when energy reaches 0
- Automatically seek energy when low (< 5 energy)

### Actions
1. **Move**: Creature moves in a direction (UP, DOWN, LEFT, RIGHT)
2. **Look**: Creature sees all neighboring entities (8 directions)
3. **Absorb**: Creature absorbs energy from adjacent energy source
4. **Depleted**: Removed when energy reaches 0

### Transaction Flow
1. Creatures decide actions each tick
2. Actions create transactions in the TransactionPool
3. Dispatcher processes all pending transactions
4. Results are recorded, completed transactions cleared

## API Usage

```python
from core.game_loop import GameLoop

# Create a new world
game = GameLoop(
    width=20,
    height=20,
    num_creatures=5,
    num_energy_sources=10
)

# Run simulation
game.run(max_ticks=100)

# Save and load
game.save("world.json")
game.load("world.json")
```

## Development

The project uses a branch-based workflow. Current development happens in the `dev` branch.

## Future Enhancements

- [ ] Visual rendering (pygame, terminal UI)
- [ ] Creature AI improvements (pathfinding, memory)
- [ ] Breeding/reproduction system
- [ ] Different creature types
- [ ] Environmental hazards
- [ ] Statistics and analytics
- [ ] Multi-threaded simulation
- [ ] Network multiplayer mode
