"""Game definitions and payoff matrices."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class Action(Enum):
    COOPERATE = "C"
    DEFECT = "D"


class Payoff(NamedTuple):
    player1: int
    player2: int


@dataclass
class Game:
    """A 2-player simultaneous game defined by its payoff matrix."""

    name: str
    description: str
    actions: tuple[Action, Action]
    # payoff[action1][action2] -> (p1_payoff, p2_payoff)
    payoff: dict[tuple[Action, Action], Payoff]

    def get_payoff(self, a1: Action, a2: Action) -> Payoff:
        return self.payoff[(a1, a2)]

    def payoff_matrix_str(self) -> str:
        """Return a human-readable payoff matrix."""
        c, d = self.actions
        def fmt(p: Payoff) -> str:
            return f"({p.player1},{p.player2})"

        lines = [
            f"  {self.name}",
            f"  {'':>14}  P2: Cooperate   P2: Defect",
            f"  P1: Cooperate   {fmt(self.payoff[(c, c)]):>14}  {fmt(self.payoff[(c, d)]):>14}",
            f"  P1: Defect      {fmt(self.payoff[(d, c)]):>14}  {fmt(self.payoff[(d, d)]):>14}",
        ]
        return "\n".join(lines)


# --- Classic Games ---

PRISONERS_DILEMMA = Game(
    name="Prisoner's Dilemma",
    description="The canonical game theory scenario. Mutual cooperation is optimal, but defection dominates.",
    actions=(Action.COOPERATE, Action.DEFECT),
    payoff={
        (Action.COOPERATE, Action.COOPERATE): Payoff(3, 3),
        (Action.COOPERATE, Action.DEFECT): Payoff(0, 5),
        (Action.DEFECT, Action.COOPERATE): Payoff(5, 0),
        (Action.DEFECT, Action.DEFECT): Payoff(1, 1),
    },
)

CHICKEN = Game(
    name="Chicken",
    description="Two drivers head toward each other. Swerve loses face, but both going straight is catastrophic.",
    actions=(Action.COOPERATE, Action.DEFECT),
    payoff={
        (Action.COOPERATE, Action.COOPERATE): Payoff(4, 4),
        (Action.COOPERATE, Action.DEFECT): Payoff(2, 5),
        (Action.DEFECT, Action.COOPERATE): Payoff(5, 2),
        (Action.DEFECT, Action.DEFECT): Payoff(0, 0),
    },
)

STAG_HUNT = Game(
    name="Stag Hunt",
    description="Cooperation yields the highest reward, but hunting hare alone is the safe bet.",
    actions=(Action.COOPERATE, Action.DEFECT),
    payoff={
        (Action.COOPERATE, Action.COOPERATE): Payoff(5, 5),
        (Action.COOPERATE, Action.DEFECT): Payoff(0, 3),
        (Action.DEFECT, Action.COOPERATE): Payoff(3, 0),
        (Action.DEFECT, Action.DEFECT): Payoff(3, 3),
    },
)

BATTLE_OF_SEXES = Game(
    name="Battle of Sexes",
    description="Two players want to coordinate but disagree on which outcome is better.",
    actions=(Action.COOPERATE, Action.DEFECT),
    payoff={
        (Action.COOPERATE, Action.COOPERATE): Payoff(3, 2),
        (Action.COOPERATE, Action.DEFECT): Payoff(0, 0),
        (Action.DEFECT, Action.COOPERATE): Payoff(0, 0),
        (Action.DEFECT, Action.DEFECT): Payoff(2, 3),
    },
)

PUBLIC_GOODS = Game(
    name="Public Goods (Hawk-Dove)",
    description="Contributing helps everyone, but free-riding is individually optimal.",
    actions=(Action.COOPERATE, Action.DEFECT),
    payoff={
        (Action.COOPERATE, Action.COOPERATE): Payoff(4, 4),
        (Action.COOPERATE, Action.DEFECT): Payoff(1, 5),
        (Action.DEFECT, Action.COOPERATE): Payoff(5, 1),
        (Action.DEFECT, Action.DEFECT): Payoff(2, 2),
    },
)

GAMES: dict[str, Game] = {
    "prisoners-dilemma": PRISONERS_DILEMMA,
    "chicken": CHICKEN,
    "stag-hunt": STAG_HUNT,
    "battle-of-sexes": BATTLE_OF_SEXES,
    "public-goods": PUBLIC_GOODS,
}
