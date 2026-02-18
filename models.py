"""
Immutable game state models and data structures.

This module defines the core data classes used to represent the game state
in a functional, immutable style.
"""
from dataclasses import dataclass
from typing import Tuple, Optional, Dict

@dataclass(frozen=True)
class Piece:
    """
    Represents a checker piece on the board.

    Attributes:
        color (str): 'R' for Red, 'B' for Black.
        is_king (bool): True if the piece has been promoted to King.
    """
    color: str
    is_king: bool = False

# Type alias for the 8x8 grid structure
BoardGrid = Tuple[Tuple[Optional[Piece], ...], ...]

@dataclass(frozen=True)
class GameState:
    """
    Represents the complete, immutable state of the game.

    Attributes:
        grid (BoardGrid): The 8x8 board configuration.
        turn (str): Current player's turn ('R' or 'B').
        p1_type (str): 'human' or 'cpu' for Player 1 (Red).
        p2_type (str): 'human' or 'cpu' for Player 2 (Black).
        current_jumper (Optional[Tuple[int, int]]): If a multi-jump sequence is active,
            this holds the position of the piece that MUST continue jumping.
        last_move (Optional[Tuple[Tuple[int, int], Tuple[int, int]]]): 
            (start, end) of the most recent move, for highlighting.
        cpu_think_start (Optional[float]): Timestamp when CPU started "thinking".
        running (bool): True if the game loop should continue.
        winner (Optional[str]): 'R' or 'B' if a player has won, else None.
        time (float): Current game time (for animations).
        hotkeys (Dict[str, tuple]): Mapping of input keys to available moves.
    """
    grid: BoardGrid
    turn: str
    p1_type: str
    p2_type: str
    current_jumper: Optional[Tuple[int, int]] = None
    last_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    cpu_think_start: Optional[float] = None
    running: bool = True
    winner: Optional[str] = None
    time: float = 0.0
    hotkeys: Dict[str, tuple] = None
