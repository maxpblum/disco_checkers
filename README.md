# Disco Checkers

A checkers game for the terminal implemented in Python. This project was developed using Gemini CLI with the Gemini 3 Flash model.

![Disco Checkers Gameplay Demo](demo.webm)

## Features

- **Dual View**: Displays the board from both the Red and Black perspectives simultaneously.
- **Hotkey Input**: Valid moves are mapped to single-character hotkeys ('1'-'9', 'a'-'z') shown on the destination squares.
- **CPU Opponent**: Option to play against a computer that selects moves at random after a short delay.
- **Visuals**: ANSI-based terminal rendering with a cycling color header, animated border, and flashing indicators for King pieces.
- **Terminal Integration**: Uses TTY raw mode for real-time input without requiring the Enter key.

## Technical Structure

The application is structured using an immutable state model and pure logic functions:

- `models.py`: Immutable `dataclass` definitions for `Piece` and `GameState`.
- `logic.py`: Functions for move generation, multi-jump validation, and state transitions.
- `rendering.py`: ANSI terminal output management, including centering and truncation.
- `utils.py`: Helpers for handling character widths and ANSI escape sequences.
- `main.py`: Entry point that manages the terminal environment and the main event loop.

## Installation and Usage

### Requirements
- Python 3.7+
- A terminal with ANSI color and Unicode support.

### Running the Game
```bash
python3 main.py
```

### Controls
- Press the displayed hotkey (e.g., `1`, `a`) to execute a move.
- Press `q` to exit.

## Testing

The codebase includes unit tests for the game logic, rendering helpers, and string utilities.

### Execute all tests
```bash
python3 -m unittest discover
```

### Test Modules
- `test_logic.py`: Standard move validation.
- `test_logic_extended.py`: Multi-jumps, King movement, and win conditions.
- `test_rendering.py`: Layout and visual effect helpers.
- `test_utils.py`: ANSI-aware string manipulation.

## License
MIT
