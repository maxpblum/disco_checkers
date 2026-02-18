"""Unit tests for the Disco Checkers rendering logic."""
import unittest
import os
import io
import sys
from unittest.mock import patch
from logic import setup_board, calculate_hotkeys, get_all_available_moves
from models import GameState
from rendering import render, get_sparkle_fg, get_chase_color
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

    def test_sparkle_effect(self):
        """Sparkle effect should change color over time."""
        # Same position, different time -> different color (eventually)
        c1 = get_sparkle_fg(0, 0.0)
        c2 = get_sparkle_fg(0, 0.5)
        self.assertNotEqual(c1, c2)

        # Same time, different position -> different color (usually)
        c3 = get_sparkle_fg(0, 0.0)
        c4 = get_sparkle_fg(1, 0.0)
        self.assertNotEqual(c3, c4)

    def test_chase_effect(self):
        """Chase effect should cycle through colors."""
        # Check that it produces valid ANSI codes
        c = get_chase_color(0, 0.0)
        self.assertTrue(c.startswith("\033["))
        
        # Check cycling
        colors = set()
        for t in range(10):
            colors.add(get_chase_color(0, t * 0.5))
        self.assertTrue(len(colors) > 1)

if __name__ == "__main__":
    unittest.main()
