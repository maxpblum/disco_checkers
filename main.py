"""
Main entry point for Disco Checkers: Imperative Shell.

This module sets up the game environment, handles user input for game mode selection,
and executes the main game loop. It manages terminal settings (raw mode) to allow
for real-time, non-blocking keyboard input and smooth rendering.
"""
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

def get_key_non_blocking() -> str | None:
    """
    Reads a single keypress from standard input without blocking.

    Uses `select` to check if input is available. If so, reads 1 byte
    and decodes it.

    Returns:
        str | None: The character read, or None if no input is available.
    """
    fd = sys.stdin.fileno()
    if select.select([sys.stdin], [], [], 0)[0]:
        try:
            return os.read(fd, 1).decode('utf-8')
        except:
            return None
    return None

def main():
    """
    Orchestrates the game initialization, loop, and cleanup.

    Steps:
    1.  Prompts user to select 'Human' or 'CPU' for both players.
    2.  Initializes the GameState (board, turn, time).
    3.  Enters 'raw' terminal mode to capture individual keystrokes.
    4.  Runs the game loop:
        - Updates game time (tick).
        - Renders the game state at ~20 FPS.
        - Checks for user input and processes it.
    5.  Restores terminal settings upon exit.
    """
    print(f"{Colors.BOLD}{Colors.RED_FG}   WELCOME TO DISCO CHECKERS   {Colors.RESET}")
    p1_h = input("Player 1 (RED)   - (h)uman or (c)pu? ").lower().startswith('h')
    p2_h = input("Player 2 (BLACK) - (h)uman or (c)pu? ").lower().startswith('h')

    grid = setup_board()
    # Initial state setup
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
        # Hide cursor and clear screen alternative buffer
        sys.stdout.write("\033[?1049h\033[H")
        sys.stdout.flush()
        
        # Set terminal to raw mode
        tty.setraw(fd)
        
        last_draw = 0
        while state.running:
            now = time.time()
            
            # Process time-based events (CPU moves, animations)
            state = process_event(state, "tick", now)
            
            # Render frame (capped at ~20 FPS)
            if now - last_draw > 0.05:
                render(state)
                last_draw = now
            
            # Check for keyboard input (non-blocking)
            if select.select([sys.stdin], [], [], 0.01)[0]:
                key = os.read(fd, 1).decode('utf-8')
                state = process_event(state, "key", key)
                
    finally:
        # Restore terminal settings and cursor
        sys.stdout.write("\033[?1049l\033[?25h")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
