"""Classic and novel game theory strategies."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections import Counter

from .games import Action


class Strategy(ABC):
    """Base class for all strategies."""

    name: str = "Base"
    description: str = ""
    author: str = ""

    def __init__(self):
        self.history: list[tuple[Action, Action]] = []  # (my_action, their_action)
        self.score: int = 0

    @abstractmethod
    def play(self, round_num: int) -> Action:
        """Choose an action for this round."""
        ...

    def record(self, my: Action, their: Action):
        self.history.append((my, their))

    def reset(self):
        self.history.clear()
        self.score = 0

    @property
    def my_actions(self) -> list[Action]:
        return [h[0] for h in self.history]

    @property
    def their_actions(self) -> list[Action]:
        return [h[1] for h in self.history]

    def __repr__(self):
        return f"{self.name}"


# --- Always Cooperate / Defect ---

class AlwaysCooperate(Strategy):
    name = "Cooperator"
    description = "Always cooperates. Naive but trusting."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        return Action.COOPERATE


class AlwaysDefect(Strategy):
    name = "Defector"
    description = "Always defects. Ruthless and rational."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        return Action.DEFECT


# --- Tit for Tat family ---

class TitForTat(Strategy):
    name = "Tit-for-Tat"
    description = "Cooperates first, then mirrors opponent's last move. The legendary Axelrod winner."
    author = "Anatol Rapoport"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.COOPERATE
        return self.their_actions[-1]


class SuspiciousTitForTat(Strategy):
    name = "Suspicious TFT"
    description = "Defects first, then mirrors. Slightly paranoid version of Tit-for-Tat."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.DEFECT
        return self.their_actions[-1]


class TitForTwoTats(Strategy):
    name = "Tit-for-Two-Tats"
    description = "Only defects after opponent defects twice in a row. More forgiving."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        if round_num < 2:
            return Action.COOPERATE
        if self.their_actions[-1] == Action.DEFECT and self.their_actions[-2] == Action.DEFECT:
            return Action.DEFECT
        return Action.COOPERATE


class TwoTitsForTat(Strategy):
    name = "Two-Tits-for-Tat"
    description = "Cooperates first, then defects twice for every opponent defection. Harsh but proportional."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.COOPERATE
        if self.their_actions[-1] == Action.DEFECT:
            return Action.DEFECT
        if round_num >= 2 and self.their_actions[-2] == Action.DEFECT:
            return Action.DEFECT
        return Action.COOPERATE


# --- Forgiving / Adaptive ---

class GenerousTitForTat(Strategy):
    name = "Generous TFT"
    description = "Like Tit-for-Tat but forgives 10% of defections. Breaks mutual defection cycles."
    author = "Nowak & Sigmund"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.COOPERATE
        if self.their_actions[-1] == Action.DEFECT:
            return Action.DEFECT if random.random() > 0.10 else Action.COOPERATE
        return Action.COOPERATE


class SoftMajority(Strategy):
    name = "Soft Majority"
    description = "Cooperates if the opponent has cooperated more than defected. Starts with cooperation."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.COOPERATE
        coop_count = sum(1 for a in self.their_actions if a == Action.COOPERATE)
        defect_count = len(self.their_actions) - coop_count
        return Action.COOPERATE if coop_count >= defect_count else Action.DEFECT


class HardMajority(Strategy):
    name = "Hard Majority"
    description = "Defects unless the opponent has cooperated more. Starts with defection."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.DEFECT
        coop_count = sum(1 for a in self.their_actions if a == Action.COOPERATE)
        defect_count = len(self.their_actions) - coop_count
        return Action.COOPERATE if coop_count > defect_count else Action.DEFECT


# --- Grim / Punishing ---

class GrimTrigger(Strategy):
    name = "Grim Trigger"
    description = "Cooperates until opponent defects once. Then defects forever. No second chances."
    author = "Friedman"

    def play(self, round_num: int) -> Action:
        if Action.DEFECT in self.their_actions:
            return Action.DEFECT
        return Action.COOPERATE


class Gradual(Strategy):
    name = "Gradual"
    description = "Cooperates, then punishes with N defections after the Nth opponent defection, followed by 2 rounds of cooperation."
    author = "Au & Nau"

    def __init__(self):
        super().__init__()
        self.punish_count = 0
        self.calming_count = 0
        self.total_defections = 0

    def play(self, round_num: int) -> Action:
        if self.punish_count > 0:
            self.punish_count -= 1
            return Action.DEFECT
        if self.calming_count > 0:
            self.calming_count -= 1
            return Action.COOPERATE
        if round_num > 0 and self.their_actions[-1] == Action.DEFECT:
            self.total_defections += 1
            self.punish_count = self.total_defections - 1
            self.calming_count = 2
            return Action.DEFECT
        return Action.COOPERATE

    def reset(self):
        super().reset()
        self.punish_count = 0
        self.calming_count = 0
        self.total_defections = 0


# --- Probabilistic / Random --

class Random(Strategy):
    name = "Random"
    description = "Flips a coin. 50/50 cooperation."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        return random.choice([Action.COOPERATE, Action.DEFECT])


class Prober(Strategy):
    name = "Prober"
    description = "Tests with D-C-C. If opponent cooperated on rounds 2-3, defects forever. Otherwise plays Tit-for-Tat."
    author = "Classic"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.DEFECT
        if round_num == 1:
            return Action.COOPERATE
        if round_num == 2:
            return Action.COOPERATE
        if round_num == 3:
            # Check if opponent cooperated on rounds 1 and 2
            if (len(self.their_actions) >= 3 and
                self.their_actions[1] == Action.COOPERATE and
                self.their_actions[2] == Action.COOPERATE):
                return Action.DEFECT  # exploit
            else:
                return self.their_actions[-1]  # Tit-for-Tat
        # After probe: if we're exploiting, keep defecting
        if (len(self.their_actions) >= 3 and
            self.their_actions[1] == Action.COOPERATE and
            self.their_actions[2] == Action.COOPERATE):
            return Action.DEFECT
        return self.their_actions[-1]


# --- Adaptive ---

class Adaptive(Strategy):
    name = "Adaptive"
    description = "Starts with cooperation, adapts strategy based on running score comparison."
    author = "Novel"

    def play(self, round_num: int) -> Action:
        if round_num < 4:
            return Action.COOPERATE
        my_recent = sum(1 for a in self.my_actions[-4:] if a == Action.COOPERATE)
        their_recent = sum(1 for a in self.their_actions[-4:] if a == Action.COOPERATE)
        if their_recent >= 3:
            return Action.COOPERATE
        if their_recent <= 1:
            return Action.DEFECT
        return Action.COOPERATE if my_recent >= 2 else Action.DEFECT


class Pavlov(Strategy):
    name = "Pavlov"
    description = "Cooperates if both players made the same move last round. Switches on difference. Win-stay, lose-shift."
    author = "Nowak & Sigmund"

    def play(self, round_num: int) -> Action:
        if round_num == 0:
            return Action.COOPERATE
        my_last = self.my_actions[-1]
        their_last = self.their_actions[-1]
        if my_last == their_last:
            return Action.COOPERATE  # stay
        return Action.DEFECT  # shift


class Handshake(Strategy):
    name = "Handshake"
    description = "Plays a specific sequence to detect copies of itself, then cooperates with them."
    author = "Roberts & Sherrerd"

    def play(self, round_num: int) -> Action:
        # Play C, D, C, D to detect mirrors
        if round_num < 4:
            return [Action.COOPERATE, Action.DEFECT, Action.COOPERATE, Action.DEFECT][round_num]
        # Check if they mirrored us
        expected = [Action.DEFECT, Action.COOPERATE, Action.DEFECT, Action.COOPERATE]
        if self.their_actions[:4] == expected:
            return Action.COOPERATE
        return Action.DEFECT


# --- Registry ---

ALL_STRATEGIES: list[type[Strategy]] = [
    AlwaysCooperate,
    AlwaysDefect,
    TitForTat,
    SuspiciousTitForTat,
    TitForTwoTats,
    TwoTitsForTat,
    GenerousTitForTat,
    SoftMajority,
    HardMajority,
    GrimTrigger,
    Gradual,
    Random,
    Prober,
    Adaptive,
    Pavlov,
    Handshake,
]

STRATEGY_MAP: dict[str, type[Strategy]] = {s.name: s for s in ALL_STRATEGIES}
