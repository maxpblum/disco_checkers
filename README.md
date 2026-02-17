# 🕺 Disco Checkers 💃

A high-fidelity, dual-perspective checkers game for the terminal. Features vibrant "disco" visuals, a "One-Touch" input system, and an immutable state-machine core.

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- A terminal with Unicode and ANSI color support.

### Running the Game
```bash
python3 main.py
```

## 🎮 How to Play

1. **Player Selection**: Choose whether Red (Player 1) and Black (Player 2) are Humans or CPU.
2. **Dual Perspective**: The screen displays two boards simultaneously—one from Red's view and one from Black's.
3. **One-Touch Input**: Valid moves are assigned hotkeys (e.g., `1`, `2`, `a`, `b`) displayed directly on the destination squares. Simply press the key to make the move. No `Enter` required!
4. **Quitting**: Press `q` at any time to exit the game.

## ✨ Disco Features

- **Animated Header**: A cycling rainbow ASCII art title.
- **Walking Lights**: An animated border of stars surrounding the board.
- **King Squares**: Squares containing Kings flash with a high-speed "yellow glow" effect.
- **Sparkle Logic**: Visual elements shift colors dynamically based on a high-frequency time-tick.

## 🛠️ Technical Architecture

The project is built using an **Immutable Core / Imperative Shell** pattern:
- `models.py`: Defines frozen `dataclass` objects for the `GameState` and `Piece`.
- `logic.py`: Contains pure functions for move calculation and state transitions.
- `rendering.py`: Handles the buffered terminal output and Unicode formatting.
- `main.py`: The imperative entry point that manages the raw TTY state and the event loop.

## 🧪 Testing

The core game logic is thoroughly verified with behavior-based unit tests.
```bash
python3 test_logic.py
```

## 📜 License
MIT
