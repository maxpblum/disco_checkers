# 🕺 Disco Checkers 💃

**Built entirely through vibe-coding using Gemini CLI with the Gemini 3 Flash model.**

A high-fidelity, dual-perspective checkers game for the terminal. Features vibrant "disco" visuals, a "One-Touch" hotkey input system, and an immutable state-machine core.

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- A terminal with Unicode and ANSI color support.

### Running the Game
```bash
python3 main.py
```

## 🎮 How to Play

1.  **Player Selection**: Choose whether Red (Player 1) and Black (Player 2) are Humans or CPU.
2.  **Dual Perspective**: The screen displays two boards simultaneously—one from Red's view and one from Black's.
3.  **One-Touch Input**: Valid moves are assigned hotkeys (e.g., `1`, `2`, `a`, `b`) displayed directly on the destination squares. Simply press the key to make the move. No `Enter` required!
4.  **Quitting**: Press `q` at any time to exit the game.

## ✨ Disco Features

-   **Animated Header**: A cycling rainbow ASCII art title.
-   **Walking Lights**: An animated border of stars surrounding the board.
-   **King Squares**: Squares containing Kings flash with a high-speed "yellow glow" effect.
-   **Sparkle Logic**: Visual elements shift colors dynamically based on a high-frequency time-tick.

## 🛠️ Technical Architecture

The project follows an **Immutable Core / Imperative Shell** pattern for high reliability and predictable state transitions:
-   `models.py`: Defines frozen `dataclass` objects for the `GameState` and `Piece`.
-   `logic.py`: Pure functions for move calculation, king promotion, and state transitions.
-   `rendering.py`: High-performance terminal rendering with ANSI-aware layout.
-   `utils.py`: ANSI-aware string utilities for width, centering, and truncation.
-   `main.py`: The imperative entry point managing raw TTY state and the event loop.

## 🧪 Testing

The core game logic, rendering helpers, and utilities are thoroughly verified with an extensive unit test suite.

### Running All Tests
```bash
python3 -m unittest discover
```

### Test Modules
-   `test_logic.py`: Basic game rules and move validation.
-   `test_logic_extended.py`: Advanced scenarios including multi-jumps, king movement, and win conditions.
-   `test_rendering.py`: Verification of visual effects and layout consistency.
-   `test_utils.py`: Validation of ANSI-aware string manipulation.

## 📜 License
MIT
