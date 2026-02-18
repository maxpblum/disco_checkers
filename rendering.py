"""
Terminal rendering and UI functions for Disco Checkers.

This module handles:
- Generating the visual representation of the checker board.
- Rendering the "Disco" chase border and sparkling text effects.
- Managing ANSI escape codes for colors and cursor positioning.
- Adapting to terminal size changes.
"""
import sys
import os
from typing import Dict, List, Tuple
from constants import Colors, SPARKLES_FG, ASCII_DISCO
from models import GameState
from logic import get_hotkey_subpos
from utils import ansi_center, ansi_ljust, visible_len, ansi_truncate

def get_sparkle_fg(idx: int, t: float) -> str:
    """
    Returns a shifting color based on position and time for a sparkling effect.

    Args:
        idx (int): The index of the character in the string.
        t (float): The current time (in seconds).

    Returns:
        str: An ANSI color escape sequence.
    """
    # Cycle through the sparkle colors based on index and time
    return SPARKLES_FG[(idx + int(t * 8)) % len(SPARKLES_FG)]

def get_chase_color(pos_idx: int, t: float) -> str:
    """
    Returns a color for the chase border that 'walks' clockwise around the screen.

    Args:
        pos_idx (int): The linear index of the border character.
        t (float): The current time (in seconds).

    Returns:
        str: An ANSI color escape sequence.
    """
    chase_colors = [Colors.MAGENTA_FG, Colors.CYAN_FG, Colors.YELLOW_FG, Colors.GREEN_FG]
    frame_offset = int(t * 6)
    
    # Calculate the color index.
    # We subtract frame_offset to make the pattern move "forward" (clockwise) along the indices.
    return chase_colors[(pos_idx - frame_offset) % len(chase_colors)]

def render_board(state: GameState, orientation: str = 'R', sq_h: int = 3, sq_w: int = 6, 
                 hotkey_lookup: Dict[Tuple[int, int], List[Tuple[str, Tuple[int, int]]]] = None):
    """
    Generates the text buffer for a single checker board view.

    Constructs a list of strings representing the rows of the board, including
    coordinate labels, pieces, and hotkey hints.

    Args:
        state (GameState): The current game state.
        orientation (str): 'R' for Red perspective (0,0 at top-left) or 'B' for Black.
        sq_h (int): Height of a single square in lines.
        sq_w (int): Width of a single square in characters.
        hotkey_lookup (Dict): Mapping of destination positions to hotkeys.

    Returns:
        List[str]: A list of strings, one for each line of the board display.
    """
    now = state.time
    board_buffer = []
    hotkey_lookup = hotkey_lookup or {}
    
    # Determine iteration order based on orientation
    rows = range(8) if orientation == 'R' else range(7, -1, -1)
    cols = range(8) if orientation == 'R' else range(7, -1, -1)
    
    # Create column labels (0-7)
    col_labels = "  " + "".join([str(i).center(sq_w) for i in cols])
    board_buffer.append(col_labels)

    for r in rows:
        # Each board row is rendered as sq_h lines of text
        for inner_r in range(sq_h):
            # Row label on the left (only on the middle line of the square)
            row_str = f"{r} " if inner_r == sq_h // 2 else "  "
            
            for c in cols:
                # Determine background color (checkerboard pattern)
                bg = Colors.GRAY_DARK if (r + c) % 2 == 1 else Colors.GRAY_LIGHT
                piece = state.grid[r][c]
                
                # Highlight last move
                if state.last_move and (r, c) in state.last_move:
                    bg = Colors.GREEN_BG

                # Highlight Kings with flashing background
                if piece and piece.is_king:
                    if int(now * 10) % 2 == 0:
                        bg = Colors.YELLOW_BG
                
                content = ""
                row_hotkeys = {}
                
                # Check if this square is a destination for any available moves
                if (r, c) in hotkey_lookup:
                    for key, start_pos in hotkey_lookup[(r, c)]:
                        target_ir, target_ic = get_hotkey_subpos(start_pos, (r, c), orientation, sq_h, sq_w)
                        if inner_r == target_ir:
                            row_hotkeys[target_ic] = key

                # Build the square's content character by character
                skip_next = False
                for inner_c in range(sq_w):
                    if skip_next:
                        skip_next = False
                        continue
                        
                    # 1. Draw Hotkey Hint
                    if inner_c in row_hotkeys:
                        char = row_hotkeys[inner_c]
                        content += f"{bg}{Colors.YELLOW_FG}{Colors.BOLD}{char}{Colors.RESET}"
                        continue
                        
                    # 2. Draw Piece (centered)
                    if piece and inner_r == sq_h // 2:
                        pad_l = (sq_w - 2) // 2
                        if inner_c == pad_l:
                            char = "🔴" if piece.color == 'R' else "⚫"
                            content += f"{bg}{char}{Colors.RESET}"
                            skip_next = True # Emojis are often double-width
                            continue
                            
                    # 3. Draw Empty Space
                    content += f"{bg} {Colors.RESET}"
                    
                row_str += content
            board_buffer.append(row_str)
            
    return board_buffer

def render(state: GameState):
    """
    Renders the entire game UI to the terminal, including borders and animations.

    Clears the screen, draws the header, two board perspectives (side-by-side),
    status messages, and a "chasing" asterisk border.

    Args:
        state (GameState): The current game state to render.
    """
    now = state.time
    try:
        term_size = os.get_terminal_size()
        term_w, term_h = term_size.columns, term_size.lines
    except OSError:
        term_w, term_h = 120, 40

    # Hide cursor and move to home position
    sys.stdout.write("\033[?25l\033[H")
    
    inner_w = term_w - 2
    inner_h = term_h - 2
    inner_buffer = []
    
    # --- 1. Draw Header ---
    for i, line in enumerate(ASCII_DISCO):
        colored_line = "".join([f"{get_sparkle_fg(i+j, now)}{c}{Colors.RESET}" if c != " " else " " for j, c in enumerate(line)])
        truncated = ansi_truncate(colored_line, inner_w)
        inner_buffer.append(ansi_center(truncated, inner_w))

    inner_buffer.append(" " * inner_w)

    # --- 2. Prepare Hotkeys ---
    hotkey_lookup = {}
    if state.hotkeys:
        for k, mv in state.hotkeys.items():
            start_pos, dest_pos = mv[0], mv[1]
            if dest_pos not in hotkey_lookup: hotkey_lookup[dest_pos] = []
            hotkey_lookup[dest_pos].append((k, start_pos))

    # --- 3. Render Boards ---
    sq_h, sq_w = 3, 6
    board_r = render_board(state, 'R', sq_h, sq_w, hotkey_lookup)
    board_b = render_board(state, 'B', sq_h, sq_w, hotkey_lookup)
    gap = " " * 8
    
    # Calculate centering
    total_board_w = visible_len(board_r[0]) + len(gap) + visible_len(board_b[0])
    board_margin_w = max(0, (inner_w - total_board_w) // 2)
    board_left_pad = " " * board_margin_w
    
    # Render labels
    perspective_labels = ansi_ljust("PERSPECTIVE: RED", visible_len(board_r[0])) + gap + ansi_ljust("PERSPECTIVE: BLACK", visible_len(board_b[0]))
    inner_buffer.append(ansi_center(ansi_truncate(perspective_labels, inner_w), inner_w))
    
    # Render board rows side-by-side
    for row_r, row_b in zip(board_r, board_b):
        combined_row = row_r + gap + row_b
        inner_buffer.append(ansi_center(ansi_truncate(combined_row, inner_w), inner_w))
    
    inner_buffer.append(" " * inner_w)
    
    # --- 4. Status Messages ---
    if state.winner:
        status = f"GAME OVER! {'RED' if state.winner == 'R' else 'BLACK'} WINS! Press any key."
    else:
        color_name = "RED" if state.turn == 'R' else "BLACK"
        player_type = (state.p1_type if state.turn=='R' else state.p2_type).upper()
        status = f"Turn: {color_name} ({player_type})"
    
    inner_buffer.append(ansi_center(ansi_truncate(status, inner_w), inner_w))
    inner_buffer.append(ansi_center(ansi_truncate("Press 'q' to Quit", inner_w), inner_w))

    # Pad with empty lines to fill screen height
    while len(inner_buffer) < inner_h:
        inner_buffer.append(" " * inner_w)
    inner_buffer = inner_buffer[:inner_h]

    # --- 5. Draw Chase Border ---
    final_output = []
    perimeter_len = 2 * term_w + 2 * (term_h - 2)
    
    # Top Border
    top_line = ""
    for x in range(term_w):
        top_line += f"{get_chase_color(x, now)}*{Colors.RESET}"
    final_output.append(top_line + "\r\n")

    # Side Borders + Content
    for y in range(inner_h):
        left_idx = perimeter_len - y - 1
        left_star = f"{get_chase_color(left_idx, now)}*{Colors.RESET}"
        
        right_idx = term_w + y
        right_star = f"{get_chase_color(right_idx, now)}*{Colors.RESET}"
        
        line_content = inner_buffer[y] if y < len(inner_buffer) else (" " * inner_w)
        if visible_len(line_content) > inner_w:
             line_content = line_content[:inner_w] 
             
        final_output.append(left_star + line_content + right_star + "\r\n")

    # Bottom Border
    bottom_line = ""
    for x in range(term_w):
        idx = (term_w + term_h - 2) + (term_w - 1 - x)
        bottom_line += f"{get_chase_color(idx, now)}*{Colors.RESET}"
    
    final_output.append(bottom_line)

    sys.stdout.write("".join(final_output))
    sys.stdout.flush()
