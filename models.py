"""Immutable game state models and data structures."""
from dataclasses import dataclass
from typing import Tuple, Optional, Dict

@dataclass(frozen=True)
class Piece:
    """Represents a checker piece."""
    color: str  # 'R' (Red) or 'B' (Black)
    is_king: bool = False

BoardGrid = Tuple[Tuple[Optional[Piece], ...], ...]

@dataclass(frozen=True)
class GameState:
    """Represents the complete, immutable state of the game."""
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
