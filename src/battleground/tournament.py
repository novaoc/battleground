"""Tournament engine — round-robin and evolutionary competitions."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .games import Action, Game
from .strategies import Strategy, ALL_STRATEGIES


@dataclass
class MatchResult:
    """Result of a single match between two strategies."""
    strategy_a: str
    strategy_b: str
    score_a: int
    score_b: int
    rounds: int
    history_a: list[Action]
    history_b: list[Action]

    @property
    def winner(self) -> str | None:
        if self.score_a > self.score_b:
            return self.strategy_a
        elif self.score_b > self.score_a:
            return self.strategy_b
        return None


@dataclass
class StrategyStats:
    """Aggregate stats for a strategy across the tournament."""
    name: str
    total_score: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    cooperation_rate: float = 0.0
    matches: int = 0

    @property
    def avg_score(self) -> float:
        return self.total_score / self.matches if self.matches else 0


def play_match(
    game: Game,
    strategy_a: Strategy,
    strategy_b: Strategy,
    rounds: int = 200,
    noise: float = 0.0,
) -> MatchResult:
    """Play a match between two strategies over N rounds."""
    strategy_a.reset()
    strategy_b.reset()

    coop_a = 0
    coop_b = 0
    hist_a: list[Action] = []
    hist_b: list[Action] = []

    for r in range(rounds):
        action_a = strategy_a.play(r)
        action_b = strategy_b.play(r)

        # Apply noise (random action flip)
        if noise > 0:
            if random.random() < noise:
                action_a = Action.DEFECT if action_a == Action.COOPERATE else Action.COOPERATE
            if random.random() < noise:
                action_b = Action.DEFECT if action_b == Action.COOPERATE else Action.COOPERATE

        payoff = game.get_payoff(action_a, action_b)
        strategy_a.score += payoff.player1
        strategy_b.score += payoff.player2

        strategy_a.record(action_a, action_b)
        strategy_b.record(action_b, action_a)

        hist_a.append(action_a)
        hist_b.append(action_b)
        if action_a == Action.COOPERATE:
            coop_a += 1
        if action_b == Action.COOPERATE:
            coop_b += 1

    return MatchResult(
        strategy_a=strategy_a.name,
        strategy_b=strategy_b.name,
        score_a=strategy_a.score,
        score_b=strategy_b.score,
        rounds=rounds,
        history_a=hist_a,
        history_b=hist_b,
    )


def run_tournament(
    game: Game,
    strategy_names: list[str] | None = None,
    rounds: int = 200,
    noise: float = 0.0,
) -> tuple[list[StrategyStats], list[MatchResult]]:
    """Run a round-robin tournament. Returns ranked stats and all match results."""
    from .strategies import STRATEGY_MAP

    if strategy_names:
        classes = [STRATEGY_MAP[n] for n in strategy_names]
    else:
        classes = ALL_STRATEGIES

    # Create strategy instances
    strategies = [cls() for cls in classes]
    stats: dict[str, StrategyStats] = {
        s.name: StrategyStats(name=s.name) for s in strategies
    }

    all_matches: list[MatchResult] = []

    for i, s_a in enumerate(strategies):
        for j, s_b in enumerate(strategies):
            if j <= i:
                continue  # each pair plays once (symmetric games)

            # Fresh instances for each match
            inst_a = type(s_a)()
            inst_b = type(s_b)()

            result = play_match(game, inst_a, inst_b, rounds=rounds, noise=noise)
            all_matches.append(result)

            # Update stats
            stats[s_a.name].total_score += result.score_a
            stats[s_b.name].total_score += result.score_b
            stats[s_a.name].matches += 1
            stats[s_b.name].matches += 1

            coop_a = sum(1 for a in result.history_a if a == Action.COOPERATE)
            coop_b = sum(1 for a in result.history_b if a == Action.COOPERATE)
            stats[s_a.name].cooperation_rate += coop_a / result.rounds
            stats[s_b.name].cooperation_rate += coop_b / result.rounds

            if result.winner == s_a.name:
                stats[s_a.name].wins += 1
                stats[s_b.name].losses += 1
            elif result.winner == s_b.name:
                stats[s_b.name].wins += 1
                stats[s_a.name].losses += 1
            else:
                stats[s_a.name].draws += 1
                stats[s_b.name].draws += 1

    # Average cooperation rates
    for s in stats.values():
        if s.matches:
            s.cooperation_rate /= s.matches

    # Sort by average score descending
    ranked = sorted(stats.values(), key=lambda s: s.avg_score, reverse=True)
    return ranked, all_matches


def run_evolutionary(
    game: Game,
    strategy_names: list[str] | None = None,
    generations: int = 50,
    population_size: int = 100,
    rounds_per_match: int = 50,
    noise: float = 0.0,
) -> list[dict]:
    """Run an evolutionary tournament — strategies replicate based on fitness."""
    from .strategies import STRATEGY_MAP

    if strategy_names:
        classes = [STRATEGY_MAP[n] for n in strategy_names]
    else:
        classes = ALL_STRATEGIES

    # Initialize population (equal distribution)
    population: list[str] = []
    per_strategy = population_size // len(classes)
    for cls in classes:
        population.extend([cls.name] * per_strategy)
    # Fill remainder
    while len(population) < population_size:
        population.append(random.choice(classes).name)

    history: list[dict] = []

    for gen in range(generations):
        # Count population
        counts: dict[str, int] = {}
        for s in population:
            counts[s] = counts.get(s, 0) + 1

        # Record generation
        history.append({
            "generation": gen,
            "counts": dict(counts),
            "dominant": max(counts, key=counts.get),
        })

        # Play round-robin within population (sample pairs)
        fitness: dict[str, float] = {s: 0.0 for s in counts}
        match_count: dict[str, int] = {s: 0 for s in counts}

        # Each individual plays a sample of opponents
        num_matches = min(len(population) // 2, 50)
        for _ in range(num_matches):
            i, j = random.sample(range(len(population)), 2)
            cls_a = STRATEGY_MAP[population[i]]
            cls_b = STRATEGY_MAP[population[j]]
            inst_a = cls_a()
            inst_b = cls_b()
            result = play_match(game, inst_a, inst_b, rounds=rounds_per_match, noise=noise)

            fitness[population[i]] += result.score_a
            fitness[population[j]] += result.score_b
            match_count[population[i]] += 1
            match_count[population[j]] += 1

        # Normalize fitness
        for s in fitness:
            if match_count[s] > 0:
                fitness[s] /= match_count[s]

        # Reproduction: fitness-proportional selection
        if not fitness or all(v == 0 for v in fitness.values()):
            break

        total_fitness = sum(fitness[s] * counts.get(s, 0) for s in fitness)
        if total_fitness <= 0:
            break

        new_population = []
        strategies_list = list(fitness.keys())
        weights = [fitness[s] * counts.get(s, 0) for s in strategies_list]
        total_w = sum(weights)
        if total_w == 0:
            break
        weights = [w / total_w for w in weights]

        for _ in range(population_size):
            chosen = random.choices(strategies_list, weights=weights, k=1)[0]
            new_population.append(chosen)

        population = new_population

    # Final generation
    counts: dict[str, int] = {}
    for s in population:
        counts[s] = counts.get(s, 0) + 1
    history.append({
        "generation": generations,
        "counts": counts,
        "dominant": max(counts, key=counts.get),
    })

    return history
