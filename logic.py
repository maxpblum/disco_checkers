"""Core game logic and state transition functions."""
import random
from dataclasses import replace
from typing import Tuple, List, Optional, Dict
from models import Piece, GameState, BoardGrid
from constants import POSSIBLE_KEYS

def setup_board() -> BoardGrid:
    """Creates the initial checker board configuration."""
    grid = [[None for _ in range(8)] for _ in range(8)]
    for r in range(3):
        for c in range(8):
            if (r + c) % 2 == 1: grid[r][c] = Piece('B')
    for r in range(5, 8):
        for c in range(8):
            if (r + c) % 2 == 1: grid[r][c] = Piece('R')
    return tuple(tuple(row) for row in grid)

def is_valid_pos(pos: Tuple[int, int]) -> bool:
    """Checks if a given (row, col) position is within board boundaries."""
    return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

def get_piece_moves(grid: BoardGrid, pos: Tuple[int, int]) -> Tuple[List[tuple], List[tuple]]:
    """Calculates all possible jumps and slides for a piece at a given position."""
    r, c = pos
    piece = grid[r][c]
    if not piece: return [], []
    jumps, moves = [], []
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece.is_king else \
           [(-1, -1), (-1, 1)] if piece.color == 'R' else [(1, -1), (1, 1)]
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if is_valid_pos((nr, nc)):
            target = grid[nr][nc]
            if target is None: moves.append((pos, (nr, nc)))
            elif target.color != piece.color:
                jr, jc = nr + dr, nc + dc
                if is_valid_pos((jr, jc)) and grid[jr][jc] is None:
                    jumps.append((pos, (jr, jc), (nr, nc)))
    return jumps, moves

def get_all_available_moves(grid: BoardGrid, turn: str, current_jumper: Optional[Tuple[int, int]]) -> List[tuple]:
    """Retrieves all legal moves for the current player's turn."""
    if current_jumper:
        jumps, _ = get_piece_moves(grid, current_jumper)
        return jumps
    all_jumps, all_moves = [], []
    for r in range(8):
        for c in range(8):
            piece = grid[r][c]
            if piece and piece.color == turn:
                p_jumps, p_moves = get_piece_moves(grid, (r, c))
                all_jumps.extend(p_jumps)
                all_moves.extend(p_moves)
    return all_jumps if all_jumps else all_moves

def calculate_hotkeys(moves: List[tuple]) -> Dict[str, tuple]:
    """Maps legal moves to single-character hotkeys for input."""
    return {POSSIBLE_KEYS[i]: moves[i] for i in range(min(len(moves), len(POSSIBLE_KEYS)))}

def execute_move(state: GameState, move: tuple) -> GameState:
    """Transitions game state by applying a move to the board."""
    start, end = move[0], move[1]
    new_grid = [list(row) for row in state.grid]
    piece = new_grid[start[0]][start[1]]
    new_grid[start[0]][start[1]] = None
    new_grid[end[0]][end[1]] = piece
    if len(move) == 3:
        new_grid[move[2][0]][move[2][1]] = None
    kinged = False
    if piece.color == 'R' and end[0] == 0 and not piece.is_king:
        new_grid[end[0]][end[1]] = replace(piece, is_king=True); kinged = True
    elif piece.color == 'B' and end[0] == 7 and not piece.is_king:
        new_grid[end[0]][end[1]] = replace(piece, is_king=True); kinged = True
    final_grid = tuple(tuple(row) for row in new_grid)
    # Check for double jump
    if len(move) == 3 and not kinged:
        next_jumps, _ = get_piece_moves(final_grid, end)
        if next_jumps:
            return replace(state, grid=final_grid, current_jumper=end, last_move=(start, end),
                           hotkeys=calculate_hotkeys(next_jumps), cpu_think_start=None)

    # Next turn
    next_turn = 'B' if state.turn == 'R' else 'R'
    next_moves = get_all_available_moves(final_grid, next_turn, None)
    
    # Check win/loss (next player has no moves)
    winner = state.turn if not next_moves else None

    return replace(state, grid=final_grid, turn=next_turn, current_jumper=None, 
                   last_move=(start, end), winner=winner, cpu_think_start=None,
                   hotkeys=calculate_hotkeys(next_moves))

def process_event(state: GameState, event_type: str, data=None) -> GameState:
    """Processes time ticks and keyboard input to update game state."""
    if event_type == "tick":
        now = data
        new_state = replace(state, time=now)
        current_type = new_state.p1_type if new_state.turn == 'R' else new_state.p2_type
        if new_state.running and not new_state.winner and current_type == 'cpu':
            if new_state.cpu_think_start is None: return replace(new_state, cpu_think_start=now)
            if now - new_state.cpu_think_start > 1.0:
                moves = list(new_state.hotkeys.values())
                if moves: return execute_move(new_state, random.choice(moves))
        return new_state
    if event_type == "key":
        if data == 'q' or state.winner: return replace(state, running=False)
        current_type = state.p1_type if state.turn == 'R' else state.p2_type
        if current_type == 'human' and data in state.hotkeys:
            return execute_move(state, state.hotkeys[data])
    return state
