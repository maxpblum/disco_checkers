"""
Core game logic and state transition functions for Disco Checkers.

This module handles:
- Board setup and initialization.
- Move validation and generation (including jumps and king promotions).
- Game state transitions (executing moves, switching turns).
- Win condition checking.
- Input processing (keyboard and time-based events).
"""
import random
from dataclasses import replace
from typing import Tuple, List, Optional, Dict
from models import Piece, GameState, BoardGrid
from constants import POSSIBLE_KEYS

def setup_board() -> BoardGrid:
    """
    Creates the initial checker board configuration.

    The board is an 8x8 grid.
    - Rows 0-2 are filled with Black pieces ('B') on dark squares.
    - Rows 5-7 are filled with Red pieces ('R') on dark squares.
    - Dark squares are those where (row + col) is odd.

    Returns:
        BoardGrid: A tuple of tuples representing the 8x8 grid, where each cell
                   contains a Piece object or None.
    """
    grid = [[None for _ in range(8)] for _ in range(8)]
    # Place Black pieces
    for r in range(3):
        for c in range(8):
            if (r + c) % 2 == 1: grid[r][c] = Piece('B')
    # Place Red pieces
    for r in range(5, 8):
        for c in range(8):
            if (r + c) % 2 == 1: grid[r][c] = Piece('R')
    return tuple(tuple(row) for row in grid)

def is_valid_pos(pos: Tuple[int, int]) -> bool:
    """
    Checks if a given (row, col) position is within board boundaries.

    Args:
        pos (Tuple[int, int]): The coordinates to check.

    Returns:
        bool: True if the position is within the 0-7 range for both row and col.
    """
    return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

def get_piece_moves(grid: BoardGrid, pos: Tuple[int, int]) -> Tuple[List[tuple], List[tuple]]:
    """
    Calculates all possible jumps and slides for a piece at a given position.

    Args:
        grid (BoardGrid): The current state of the board.
        pos (Tuple[int, int]): The (row, col) of the piece to move.

    Returns:
        Tuple[List[tuple], List[tuple]]: A pair of lists:
            - jumps: A list of jump moves. Each move is a tuple: (start, end, captured_pos).
            - moves: A list of slide moves. Each move is a tuple: (start, end).
    """
    r, c = pos
    piece = grid[r][c]
    if not piece: return [], []
    
    jumps, moves = [], []
    
    # Determine movement directions based on piece type and color
    # Kings move in all 4 diagonals.
    # Red moves "up" (decreasing row index).
    # Black moves "down" (increasing row index).
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece.is_king else \
           [(-1, -1), (-1, 1)] if piece.color == 'R' else [(1, -1), (1, 1)]
           
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        
        if is_valid_pos((nr, nc)):
            target = grid[nr][nc]
            
            # 1. Slide to empty square
            if target is None:
                moves.append((pos, (nr, nc)))
            
            # 2. Jump over opponent
            elif target.color != piece.color:
                jr, jc = nr + dr, nc + dc # Jump destination
                if is_valid_pos((jr, jc)) and grid[jr][jc] is None:
                    jumps.append((pos, (jr, jc), (nr, nc)))
                    
    return jumps, moves

def get_all_available_moves(grid: BoardGrid, turn: str, current_jumper: Optional[Tuple[int, int]]) -> List[tuple]:
    """
    Retrieves all legal moves for the current player's turn.

    Enforces the "forced jump" rule: if any jump is available, the player MUST jump.
    Slides are only allowed if no jumps exist on the board.

    Args:
        grid (BoardGrid): The current board state.
        turn (str): The color of the current player ('R' or 'B').
        current_jumper (Optional[Tuple[int, int]]): If a piece is in the middle of a
            multi-jump chain, only moves for this piece are considered.

    Returns:
        List[tuple]: A list of legal moves. Each move is a tuple (start, end) or (start, end, captured).
    """
    # If a piece just jumped and can jump again, it MUST continue jumping.
    if current_jumper:
        jumps, _ = get_piece_moves(grid, current_jumper)
        return jumps

    all_jumps, all_moves = [], []
    
    # Scan the entire board for the current player's pieces
    for r in range(8):
        for c in range(8):
            piece = grid[r][c]
            if piece and piece.color == turn:
                p_jumps, p_moves = get_piece_moves(grid, (r, c))
                all_jumps.extend(p_jumps)
                all_moves.extend(p_moves)
    
    # Forced Jump Rule: If jumps exist, ignore slides.
    return all_jumps if all_jumps else all_moves

def calculate_hotkeys(moves: List[tuple]) -> Dict[str, tuple]:
    """
    Maps legal moves to single-character hotkeys for input.

    Assigns keys from '1' to 'z' to the available moves.

    Args:
        moves (List[tuple]): The list of legal moves.

    Returns:
        Dict[str, tuple]: A mapping from key char (e.g., '1') to the move tuple.
    """
    return {POSSIBLE_KEYS[i]: moves[i] for i in range(min(len(moves), len(POSSIBLE_KEYS)))}

def get_hotkey_subpos(start: Tuple[int, int], end: Tuple[int, int], orientation: str, sq_h: int, sq_w: int) -> Tuple[int, int]:
    """
    Calculates the (inner_r, inner_c) coordinate within a board square to display the hotkey.

    The hotkey is placed in the corner of the destination square that is physically closest
    to the starting square, providing a visual cue for direction.

    Args:
        start (Tuple[int, int]): The move's starting board coordinates.
        end (Tuple[int, int]): The move's destination board coordinates.
        orientation (str): The board's visual orientation ('R' or 'B').
        sq_h (int): Height of a single board square in characters.
        sq_w (int): Width of a single board square in characters.

    Returns:
        Tuple[int, int]: The (row, col) offset within the destination square's character grid.
    """
    sr, sc = start
    er, ec = end
    
    # Determine visual direction based on orientation
    if orientation == 'R':
        # Red perspective: (0,0) is top-left.
        ir = 0 if sr < er else sq_h - 1
        ic = 0 if sc < ec else sq_w - 1
    else:
        # Black perspective: (7,7) is top-left (visually rotated 180).
        # We need to invert the logic because the rendering loop iterates differently.
        ir = 0 if sr > er else sq_h - 1
        ic = 0 if sc > ec else sq_w - 1
        
    return ir, ic

def execute_move(state: GameState, move: tuple) -> GameState:
    """
    Transitions the game state by applying a chosen move to the board.

    Handles:
    - Moving the piece.
    - Removing captured pieces (if jump).
    - King promotion (reaching the far end).
    - Multi-jump chaining (checking for double jumps).
    - Switching turns.
    - Checking for win/loss (no moves left).

    Args:
        state (GameState): The current game state.
        move (tuple): The move to execute.

    Returns:
        GameState: The new game state after the move.
    """
    start, end = move[0], move[1]
    
    # 1. Update the grid
    new_grid = [list(row) for row in state.grid]
    piece = new_grid[start[0]][start[1]]
    
    # Move piece
    new_grid[start[0]][start[1]] = None
    new_grid[end[0]][end[1]] = piece
    
    # Remove captured piece if it's a jump
    if len(move) == 3:
        new_grid[move[2][0]][move[2][1]] = None
        
    # 2. Check for King Promotion
    kinged = False
    if piece.color == 'R' and end[0] == 0 and not piece.is_king:
        new_grid[end[0]][end[1]] = replace(piece, is_king=True)
        kinged = True
    elif piece.color == 'B' and end[0] == 7 and not piece.is_king:
        new_grid[end[0]][end[1]] = replace(piece, is_king=True)
        kinged = True
        
    final_grid = tuple(tuple(row) for row in new_grid)

    # 3. Check for Multi-Jump
    # If it was a jump, and not just promoted (promotion ends turn), check for more jumps.
    if len(move) == 3 and not kinged:
        next_jumps, _ = get_piece_moves(final_grid, end)
        if next_jumps:
            # Player gets another turn, constrained to this piece
            return replace(state, 
                           grid=final_grid, 
                           current_jumper=end, 
                           last_move=(start, end),
                           hotkeys=calculate_hotkeys(next_jumps), 
                           cpu_think_start=None)

    # 4. Switch Turn
    next_turn = 'B' if state.turn == 'R' else 'R'
    next_moves = get_all_available_moves(final_grid, next_turn, None)
    
    # 5. Check Win Condition
    # If the next player has no legal moves, the current player wins.
    winner = state.turn if not next_moves else None

    return replace(state, 
                   grid=final_grid, 
                   turn=next_turn, 
                   current_jumper=None, 
                   last_move=(start, end), 
                   winner=winner, 
                   cpu_think_start=None,
                   hotkeys=calculate_hotkeys(next_moves))

def process_event(state: GameState, event_type: str, data=None) -> GameState:
    """
    Processes external events (time ticks, keyboard input) to update game state.

    Args:
        state (GameState): The current game state.
        event_type (str): "tick" or "key".
        data (Any): The timestamp (float) for "tick", or key char (str) for "key".

    Returns:
        GameState: The updated game state.
    """
    # Handle Time Tick
    if event_type == "tick":
        now = data
        new_state = replace(state, time=now)
        
        # CPU Logic Handling
        current_type = new_state.p1_type if new_state.turn == 'R' else new_state.p2_type
        if new_state.running and not new_state.winner and current_type == 'cpu':
            # Initialize think timer if not started
            if new_state.cpu_think_start is None: 
                return replace(new_state, cpu_think_start=now)
            
            # Execute move after 1 second delay
            if now - new_state.cpu_think_start > 1.0:
                moves = list(new_state.hotkeys.values())
                if moves: 
                    return execute_move(new_state, random.choice(moves))
                    
        return new_state

    # Handle Keyboard Input
    if event_type == "key":
        if data == 'q' or state.winner: 
            return replace(state, running=False)
            
        current_type = state.p1_type if state.turn == 'R' else state.p2_type
        if current_type == 'human' and data in state.hotkeys:
            return execute_move(state, state.hotkeys[data])
            
    return state
