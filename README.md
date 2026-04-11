# ⚔️ Battleground

Game theory tournament simulator. Run round-robin and evolutionary tournaments with classic strategies.

```
  ╔══════════════════════════════════════════════════════════╗
  ║  ⚔️  BATTLEGROUND — Game Theory Tournament Simulator     ║
  ╚══════════════════════════════════════════════════════════╝

  Game:    Prisoner's Dilemma
  Rounds:  200 per match

  ══════════════════════════════════════════════════════
  📊  TOURNAMENT RESULTS
  ══════════════════════════════════════════════════════

  #    Strategy               Avg Score    W    L    D  Coop%     Chart
  ──── ────────────────────── ────────── ──── ──── ──── ───────  ────────────────────
  🥇   Tit-for-Two-Tats            504.3   12    1    2  87.3%  ████████████████████
  🥈   Pavlov                       499.8   11    2    2  81.5%  ███████████████████▉
  🥉   Tit-for-Tat                 498.1   10    3    2  85.2%  ███████████████████▉
```

## Install

```bash
pip install battleground
```

Or run from source:

```bash
git clone https://github.com/novaoc/battleground.git
cd battleground
pip install -e .
```

## Usage

### Run a tournament (default: Prisoner's Dilemma)

```bash
battleground
```

### Choose a game

```bash
battleground -g chicken
battleground -g stag-hunt
battleground -g battle-of-sexes
battleground -g public-goods
```

### Evolutionary tournament

Watch strategies compete over generations — the fittest replicate, the weak die out:

```bash
battleground --evolve
battleground --evolve --generations 100 --population 200
```

### Add noise

Simulate miscommunication — 5% chance each action gets flipped:

```bash
battleground -n 0.05
```

### Select strategies

```bash
battleground --strategies "Tit-for-Tat,Defector,Cooperator,Grim Trigger"
```

### JSON output

```bash
battleground --json | jq '.rankings[0]'
```

## Games

| Game | Description |
|------|-------------|
| `prisoners-dilemma` | The canonical game. Mutual cooperation is optimal, but defection dominates. |
| `chicken` | Two drivers head toward each other. Swerving loses face. |
| `stag-hunt` | Cooperation yields the highest reward, but hunting hare is the safe bet. |
| `battle-of-sexes` | Two players want to coordinate but disagree on which outcome is better. |
| `public-goods` | Contributing helps everyone, but free-riding is individually optimal. |

## Strategies (16 included)

### Classic
- **Cooperator** — Always cooperates
- **Defector** — Always defects
- **Random** — 50/50 coin flip

### Tit-for-Tat Family
- **Tit-for-Tat** — Cooperates first, then mirrors (Axelrod's champion)
- **Suspicious TFT** — Defects first, then mirrors
- **Tit-for-Two-Tats** — Only punishes after two consecutive defections
- **Two-Tits-for-Tat** — Defects twice for every opponent defection
- **Generous TFT** — Forgives 10% of defections

### Punishing
- **Grim Trigger** — Cooperates until betrayed, then defects forever
- **Gradual** — Escalating punishment: N defections for the Nth betrayal

### Adaptive
- **Soft Majority** — Goes with what most opponents do
- **Hard Majority** — Defects unless opponent has been majority cooperative
- **Adaptive** — Adapts based on recent score comparison
- **Pavlov** — Win-stay, lose-shift

### Advanced
- **Prober** — Tests opponent, exploits if they're too forgiving
- **Handshake** — Detects copies of itself via a specific opening sequence

## Why?

Game theory is everywhere — crypto protocol design, market dynamics, evolutionary biology, AI alignment. The Prisoner's Dilemma isn't just a thought experiment; it's the mathematical foundation of cooperation itself.

Battleground makes these dynamics tangible. Run a tournament, see who wins, then add noise and watch everything fall apart — just like real life.

## License

MIT
