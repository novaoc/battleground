"""Terminal display with rich formatting."""

from __future__ import annotations

import sys
from .games import Action, Game
from .tournament import MatchResult, StrategyStats


def _bar(value: float, max_val: float, width: int = 20, char: str = "█") -> str:
    """Render a bar chart element."""
    if max_val == 0:
        return ""
    filled = int((value / max_val) * width)
    return char * filled


def display_header(game: Game, rounds: int, noise: float):
    """Print tournament header."""
    print()
    print(f"  ╔══════════════════════════════════════════════════════════╗")
    print(f"  ║  ⚔️  BATTLEGROUND — Game Theory Tournament Simulator     ║")
    print(f"  ╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  Game:    {game.name}")
    print(f"  Rounds:  {rounds} per match")
    if noise > 0:
        print(f"  Noise:   {noise:.1%}")
    print()
    print(game.payoff_matrix_str())
    print()


def display_rankings(ranked: list[StrategyStats]):
    """Print ranked results with bar charts."""
    print("  ══════════════════════════════════════════════════════")
    print("  📊  TOURNAMENT RESULTS")
    print("  ══════════════════════════════════════════════════════")
    print()
    print(f"  {'#':<4} {'Strategy':<22} {'Avg Score':>10} {'W':>4} {'L':>4} {'D':>4} {'Coop%':>7}  Chart")
    print(f"  {'─'*4} {'─'*22} {'─'*10} {'─'*4} {'─'*4} {'─'*4} {'─'*7}  {'─'*20}")

    max_avg = max(s.avg_score for s in ranked) if ranked else 1

    for i, s in enumerate(ranked):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f" {i+1}"
        bar = _bar(s.avg_score, max_avg, width=20)
        print(
            f"  {medal:<4} {s.name:<22} {s.avg_score:>10.1f} "
            f"{s.wins:>4} {s.losses:>4} {s.draws:>4} {s.cooperation_rate:>6.1%}  {bar}"
        )

    print()


def display_evolution(history: list[dict]):
    """Print evolutionary tournament timeline."""
    print("  ══════════════════════════════════════════════════════")
    print("  🧬  EVOLUTIONARY TOURNAMENT")
    print("  ══════════════════════════════════════════════════════")
    print()

    # Collect all strategy names that appeared
    all_strategies = set()
    for gen in history:
        all_strategies.update(gen["counts"].keys())
    all_strategies = sorted(all_strategies)

    # Print header
    gen_col = f"  {'Gen':>4}"
    cols = [f"{s[:10]:>10}" for s in all_strategies]
    print(f"{gen_col} {''.join(cols)}  {'Dominant':<16}")
    print(f"  {'─'*4} {''.join(['─'*10 for _ in all_strategies])}  {'─'*16}")

    # Print every Nth generation + first and last
    total = len(history)
    step = max(1, total // 20)
    indices = list(range(0, total, step))
    if total - 1 not in indices:
        indices.append(total - 1)

    for idx in indices:
        gen = history[idx]
        counts = gen["counts"]
        total_pop = sum(counts.values())
        vals = [f"{counts.get(s, 0):>10}" for s in all_strategies]
        dominant = gen.get("dominant", "?")
        print(f"  {gen['generation']:>4} {''.join(vals)}  {dominant:<16}")

    print()

    # Final population chart
    final = history[-1]["counts"]
    total_pop = sum(final.values())
    print("  Final Population:")
    for name, count in sorted(final.items(), key=lambda x: -x[1]):
        pct = count / total_pop * 100
        bar = _bar(count, total_pop, width=30)
        print(f"    {name:<22} {count:>4} ({pct:>5.1f}%) {bar}")
    print()


def display_match_detail(result: MatchResult, max_rounds_shown: int = 20):
    """Print detailed match history."""
    print(f"\n  {result.strategy_a} vs {result.strategy_b}")
    print(f"  Score: {result.score_a} - {result.score_b}")
    if result.winner:
        print(f"  Winner: {result.winner}")
    else:
        print(f"  Result: Draw")

    if result.rounds <= max_rounds_shown:
        print(f"\n  {'Round':>5}  {result.strategy_a[:10]:<10} {result.strategy_b[:10]:<10}")
        print(f"  {'─'*5}  {'─'*10} {'─'*10}")
        for r in range(result.rounds):
            a = result.history_a[r]
            b = result.history_b[r]
            a_sym = "🤝" if a == Action.COOPERATE else "⚔️"
            b_sym = "🤝" if b == Action.COOPERATE else "⚔️"
            print(f"  {r+1:>5}  {a.value:<10} {b.value:<10}  {a_sym} {b_sym}")
    print()


def display_strategy_list():
    """List all available strategies."""
    from .strategies import ALL_STRATEGIES

    print()
    print("  ══════════════════════════════════════════════════════")
    print("  📖  AVAILABLE STRATEGIES")
    print("  ══════════════════════════════════════════════════════")
    print()
    for s in ALL_STRATEGIES:
        print(f"  • {s.name:<22} — {s.description}")
    print()


def display_game_list():
    """List all available games."""
    from .games import GAMES

    print()
    print("  ══════════════════════════════════════════════════════")
    print("  🎲  AVAILABLE GAMES")
    print("  ══════════════════════════════════════════════════════")
    print()
    for name, game in GAMES.items():
        print(f"  • {name:<22} — {game.description}")
        print(f"    {game.payoff_matrix_str()}")
        print()


def output_csv_rankings(ranked: list[StrategyStats]) -> str:
    """Output tournament rankings as CSV."""
    import csv, io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["rank", "name", "avg_score", "total_score", "wins", "losses", "draws", "cooperation_rate"])
    for i, s in enumerate(ranked):
        writer.writerow([i + 1, s.name, round(s.avg_score, 2), s.total_score, s.wins, s.losses, s.draws, round(s.cooperation_rate, 4)])
    return buf.getvalue()


def output_csv_evolution(history: list[dict]) -> str:
    """Output evolutionary tournament history as CSV."""
    import csv, io

    # Collect all strategy names that appeared
    all_strategies = set()
    for gen in history:
        all_strategies.update(gen["counts"].keys())
    all_strategies = sorted(all_strategies)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["generation", "dominant"] + all_strategies)
    for gen in history:
        row = [gen["generation"], gen.get("dominant", "?")]
        row.extend(gen["counts"].get(s, 0) for s in all_strategies)
        writer.writerow(row)
    return buf.getvalue()


def output_csv_matchup(result: "MatchResult", game: "Game | None" = None) -> str:
    """Output a single match result as CSV (round by round).

    If a game object is provided, per-round scores are computed from the payoff matrix.
    """
    import csv, io
    from .games import Action

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["round", f"{result.strategy_a}_action", f"{result.strategy_b}_action", f"{result.strategy_a}_score", f"{result.strategy_b}_score"])

    running_a = 0
    running_b = 0
    for r in range(result.rounds):
        a = result.history_a[r]
        b = result.history_b[r]

        if game is not None:
            payoff = game.get_payoff(a, b)
            running_a += payoff.player1
            running_b += payoff.player2

        writer.writerow([r + 1, a.value, b.value, running_a, running_b])
    return buf.getvalue()
