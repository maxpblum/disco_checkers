"""Terminal rendering and UI functions for board visualization."""
import sys
import os
from typing import Dict
from constants import Colors, SPARKLES_FG, ASCII_DISCO
from models import GameState

def get_sparkle_fg(idx: int, t: float) -> str:
    """Returns a shifting color based on position and time."""
    return SPARKLES_FG[(idx + int(t * 8)) % len(SPARKLES_FG)]

def render_board(state: GameState, orientation: str = 'R', sq_h: int = 3, sq_w: int = 6, hotkey_lookup: Dict = None):
    """Generates the text buffer for a single checker board view."""
    now = state.time
    board_buffer = []
    hotkey_lookup = hotkey_lookup or {}
    rows = range(8) if orientation == 'R' else range(7, -1, -1)
    cols = range(8) if orientation == 'R' else range(7, -1, -1)
    col_labels = "  " + "".join([str(i).center(sq_w) for i in cols])
    board_buffer.append(col_labels)

    for r in rows:
        for inner_r in range(sq_h):
            row_str = f"{r} " if inner_r == sq_h // 2 else "  "
            for c in cols:
                bg = Colors.GRAY_DARK if (r + c) % 2 == 1 else Colors.GRAY_LIGHT
                piece = state.grid[r][c]
                if piece and piece.is_king and int(now * 10) % 2 == 0:
                    bg = Colors.YELLOW_BG
                if state.last_move and (r, c) in state.last_move:
                    bg = Colors.GREEN_BG
                
                content = " " * sq_w
                if (r, c) in hotkey_lookup and inner_r == sq_h // 2:
                    keys_str = "/".join(hotkey_lookup[(r, c)])[:sq_w]
                    pad_l = (sq_w - len(keys_str)) // 2
                    pad_r = sq_w - len(keys_str) - pad_l
                    content = (" " * pad_l) + f"{Colors.YELLOW_FG}{Colors.BOLD}{keys_str}{Colors.RESET}{bg}" + (" " * pad_r)
                elif piece and inner_r == sq_h // 2:
                    char = "🔴" if piece.color == 'R' else "⚫"
                    pad_l = (sq_w - 2) // 2
                    pad_r = sq_w - 2 - pad_l
                    content = " " * pad_l + char + " " * pad_r
                row_str += f"{bg}{content}{Colors.RESET}"
            board_buffer.append(row_str)
    return board_buffer

def render(state: GameState):
    """Renders the entire UI to terminal: header, two boards, and status."""
    now = state.time
    try:
        term_size = os.get_terminal_size()
        term_w, term_h = term_size.columns, term_size.lines
    except OSError:
        term_w, term_h = 120, 40

    sys.stdout.write("\033[?25l\033[H")
    buffer = []
    
    # Header
    for i, line in enumerate(ASCII_DISCO):
        colored_line = "".join([f"{get_sparkle_fg(i+j, now)}{c}{Colors.RESET}" if c != " " else " " for j, c in enumerate(line)])
        buffer.append(colored_line.center(term_w + (len(colored_line)-len(line))) + "\r\n")
    buffer.append("\r\n")

    hotkey_lookup = {}
    if state.hotkeys:
        for k, mv in state.hotkeys.items():
            dest = mv[1]
            if dest not in hotkey_lookup: hotkey_lookup[dest] = []
            hotkey_lookup[dest].append(k)

    sq_h, sq_w = 3, 6
    board_r = render_board(state, 'R', sq_h, sq_w, hotkey_lookup)
    board_b = render_board(state, 'B', sq_h, sq_w, hotkey_lookup)
    gap, total_w = " " * 8, (sq_w * 8 + 2) * 2 + 8
    margin = max(0, (term_w - total_w) // 2)
    
    buffer.append(" " * margin + "PERSPECTIVE: RED".center(sq_w * 8 + 2) + gap + "PERSPECTIVE: BLACK".center(sq_w * 8 + 2) + "\r\n")
    for row_r, row_b in zip(board_r, board_b):
        buffer.append(" " * margin + row_r + gap + row_b + "\r\n")
    
    buffer.append("\r\n")
    if state.winner:
        status = f"GAME OVER! {'RED' if state.winner == 'R' else 'BLACK'} WINS! Press any key to exit."
    else:
        color_name = "RED" if state.turn == 'R' else "BLACK"
        player_type = (state.p1_type if state.turn=='R' else state.p2_type).upper()
        status = f"Turn: {color_name} ({player_type})"
    
    buffer.append(status.center(term_w) + "\r\n")
    buffer.append("Press 'q' to Quit".center(term_w) + "\r\n")
    
    sys.stdout.write("".join(buffer))
    sys.stdout.flush()
