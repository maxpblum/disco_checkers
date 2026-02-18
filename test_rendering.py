"""Unit tests for the Disco Checkers rendering logic."""
import unittest
import os
import io
import sys
from unittest.mock import patch
from logic import setup_board, calculate_hotkeys, get_all_available_moves
from models import GameState
from rendering import render
from utils import visible_len, strip_ansi

class TestRendering(unittest.TestCase):
    
    def setUp(self):
        # Create a standard game state
        grid = setup_board()
        self.state = GameState(
            grid=grid,
            turn='R',
            p1_type='human',
            p2_type='cpu',
            hotkeys=calculate_hotkeys(get_all_available_moves(grid, 'R', None)),
            time=1.0
        )

    @patch('os.get_terminal_size')
    def test_line_lengths(self, mocked_size):
        """Every line in the render output must have visible length equal to term_w."""
        term_w, term_h = 100, 30
        mocked_size.return_value = os.terminal_size((term_w, term_h))
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            render(self.state)
            output = sys.stdout.getvalue()
            
            # The render starts with \033[?25l\033[H (ANSI hide/home)
            # We strip that for testing
            if output.startswith("\033[?25l\033[H"):
                output = output[len("\033[?25l\033[H"):]
            
            # Lines are joined by \r\n
            lines = output.split("\r\n")
            
            # Final number of lines should be term_h
            self.assertEqual(len(lines), term_h)
            
            for i, line in enumerate(lines):
                vlen = visible_len(line)
                self.assertEqual(vlen, term_w, f"Line {i} should be {term_w} visible chars, but is {vlen}")
        finally:
            sys.stdout = old_stdout

if __name__ == "__main__":
    unittest.main()
