"""CLI entry point for Battleground."""

import argparse
import sys

from .games import GAMES
from .strategies import ALL_STRATEGIES, STRATEGY_MAP
from .tournament import run_tournament, run_evolutionary
from .display import (
    display_header,
    display_rankings,
    display_evolution,
    display_match_detail,
    display_strategy_list,
    display_game_list,
)


def main():
    parser = argparse.ArgumentParser(
        prog="battleground",
        description="⚔️  Game theory tournament simulator — run round-robin and evolutionary tournaments with classic strategies.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  battleground                          # Run default tournament (Prisoner's Dilemma)
  battleground -g chicken               # Play Chicken game
  battleground -r 500                   # 500 rounds per match
  battleground -n 0.05                  # 5% noise (random flips)
  battleground --evolve                 # Evolutionary tournament
  battleground --evolve --generations 100  # 100 generations
  battleground --strategies "Tit-for-Tat,Defector,Cooperator"  # Select strategies
  battleground --list-strategies        # Show all strategies
  battleground --list-games             # Show all games
        """,
    )

    parser.add_argument(
        "-g", "--game",
        choices=list(GAMES.keys()),
        default="prisoners-dilemma",
        help="Game to play (default: prisoners-dilemma)",
    )
    parser.add_argument(
        "-r", "--rounds",
        type=int,
        default=200,
        help="Rounds per match (default: 200)",
    )
    parser.add_argument(
        "-n", "--noise",
        type=float,
        default=0.0,
        help="Noise probability — chance of action flip (default: 0.0)",
    )
    parser.add_argument(
        "--strategies",
        type=str,
        default=None,
        help="Comma-separated strategy names to include (default: all)",
    )
    parser.add_argument(
        "--evolve",
        action="store_true",
        help="Run evolutionary tournament instead of round-robin",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=50,
        help="Number of generations for evolutionary mode (default: 50)",
    )
    parser.add_argument(
        "--population",
        type=int,
        default=100,
        help="Population size for evolutionary mode (default: 100)",
    )
    parser.add_argument(
        "--detail",
        type=int,
        default=0,
        help="Show detailed match history for top N matchups (default: 0)",
    )
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List all available strategies",
    )
    parser.add_argument(
        "--list-games",
        action="store_true",
        help="List all available games",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results (default: random)",
    )

    args = parser.parse_args()

    if args.list_strategies:
        display_strategy_list()
        return

    if args.list_games:
        display_game_list()
        return

    # Parse strategies
    strat_names = None
    if args.strategies:
        strat_names = [s.strip() for s in args.strategies.split(",")]
        for name in strat_names:
            if name not in STRATEGY_MAP:
                print(f"  ❌ Unknown strategy: '{name}'")
                print(f"  Available: {', '.join(STRATEGY_MAP.keys())}")
                sys.exit(1)

    game = GAMES[args.game]

    if args.evolve:
        # Evolutionary tournament
        if not args.json:
            display_header(game, args.rounds, args.noise)
            print("  🧬 Running evolutionary tournament...")

        history = run_evolutionary(
            game,
            strategy_names=strat_names,
            generations=args.generations,
            population_size=args.population,
            rounds_per_match=args.rounds,
            noise=args.noise,
            seed=args.seed,
        )

        if args.json:
            import json
            data = {
                "game": args.game,
                "generations": args.generations,
                "population_size": args.population,
                "rounds_per_match": args.rounds,
                "noise": args.noise,
                "seed": args.seed,
                "history": history,
            }
            print(json.dumps(data, indent=2, default=str))
        else:
            display_evolution(history)
    else:
        # Round-robin tournament
        if not args.json:
            display_header(game, args.rounds, args.noise)
            print("  ⚔️  Running round-robin tournament...")

        ranked, matches = run_tournament(
            game,
            strategy_names=strat_names,
            rounds=args.rounds,
            noise=args.noise,
            seed=args.seed,
        )

        if args.json:
            import json
            data = {
                "game": args.game,
                "rounds": args.rounds,
                "noise": args.noise,
                "seed": args.seed,
                "rankings": [
                    {
                        "rank": i + 1,
                        "name": s.name,
                        "avg_score": round(s.avg_score, 2),
                        "total_score": s.total_score,
                        "wins": s.wins,
                        "losses": s.losses,
                        "draws": s.draws,
                        "cooperation_rate": round(s.cooperation_rate, 4),
                    }
                    for i, s in enumerate(ranked)
                ],
            }
            print(json.dumps(data, indent=2))
        else:
            display_rankings(ranked)

            if args.detail > 0:
                # Show top matchup details
                sorted_matches = sorted(matches, key=lambda m: abs(m.score_a - m.score_b), reverse=True)
                for match in sorted_matches[:args.detail]:
                    display_match_detail(match)

            # Summary
            winner = ranked[0]
            most_cooperative = max(ranked, key=lambda s: s.cooperation_rate)
            print(f"  🏆 Winner: {winner.name} (avg {winner.avg_score:.1f} per match)")
            if most_cooperative.name != winner.name:
                print(f"  🕊️  Most cooperative: {most_cooperative.name} ({most_cooperative.cooperation_rate:.1%})")
            print()


if __name__ == "__main__":
    main()
