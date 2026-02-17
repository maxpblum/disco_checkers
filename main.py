"""Main entry point for Disco Checkers: Imperative Shell."""
import time
import os
import sys
import tty
import termios
import select
from models import GameState
from logic import setup_board, get_all_available_moves, calculate_hotkeys, process_event
from rendering import render
from constants import Colors

def get_key_non_blocking():
    """Reads a single keypress from standard input without blocking."""
    fd = sys.stdin.fileno()
    if select.select([sys.stdin], [], [], 0)[0]:
        try:
            return os.read(fd, 1).decode('utf-8')
        except:
            return None
    return None

def main():
    """Orchestrates the game initialization, loop, and cleanup."""
    print(f"{Colors.BOLD}{Colors.RED_FG}   WELCOME TO DISCO CHECKERS   {Colors.RESET}")
    p1_h = input("Player 1 (RED)   - (h)uman or (c)pu? ").lower().startswith('h')
    p2_h = input("Player 2 (BLACK) - (h)uman or (c)pu? ").lower().startswith('h')

    grid = setup_board()
    state = GameState(
        grid=grid,
        turn='R',
        p1_type='human' if p1_h else 'cpu',
        p2_type='human' if p2_h else 'cpu',
        hotkeys=calculate_hotkeys(get_all_available_moves(grid, 'R', None)),
        time=time.time()
    )

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        sys.stdout.write("\033[?1049h\033[H")
        sys.stdout.flush()
        tty.setraw(fd)
        last_draw = 0
        while state.running:
            now = time.time()
            state = process_event(state, "tick", now)
            if now - last_draw > 0.05:
                render(state); last_draw = now
            if select.select([sys.stdin], [], [], 0.01)[0]:
                state = process_event(state, "key", os.read(fd, 1).decode('utf-8'))
    finally:
        sys.stdout.write("\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
