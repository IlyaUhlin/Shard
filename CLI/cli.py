import argparse
import sys

from core.game_loop import GameLoop


def main():
    parser = argparse.ArgumentParser(description="World Simulation Game")
    parser.add_argument("--width", type=int, default=20, help="World width")
    parser.add_argument("--height", type=int, default=20, help="World height")
    parser.add_argument("--creatures", type=int, default=5, help="Number of creatures")
    parser.add_argument("--energy-sources", type=int, default=10, help="Number of energy sources")
    parser.add_argument("--ticks", type=int, default=100, help="Maximum number of ticks")
    parser.add_argument("--save", type=str, help="Save world to file after simulation")
    parser.add_argument("--load", type=str, help="Load world from file before simulation")
    
    args = parser.parse_args()

    if args.load:
        game = GameLoop.__new__(GameLoop)
        if game.load(args.load):
            game.run(max_ticks=args.ticks)
            if args.save:
                game.save(args.save)
    else:
        game = GameLoop(
            width=args.width,
            height=args.height,
            num_creatures=args.creatures,
            num_energy_sources=args.energy_sources
        )
        game.run(max_ticks=args.ticks)
        if args.save:
            game.save(args.save)


if __name__ == "__main__":
    main()