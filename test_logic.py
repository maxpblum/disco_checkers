"""Unit tests for the Disco Checkers core logic."""
import unittest
from dataclasses import replace
from logic import setup_board, execute_move, is_valid_pos, get_piece_moves, get_hotkey_subpos
from models import Piece, GameState

def create_mock_state(grid, turn='R'):
    """Helper to construct a GameState with minimal boilerplate."""
    return GameState(
        grid=tuple(tuple(row) for row in grid),
        turn=turn,
        p1_type='human',
        p2_type='cpu',
        hotkeys={}
    )

def empty_grid():
    """Helper to return an empty 8x8 checker board grid."""
    return [[None for _ in range(8)] for _ in range(8)]

class TestCheckersLogic(unittest.TestCase):
    
    def test_hotkey_corner_placement(self):
        """Hotkey should be placed in the corner nearest the origin, accounting for board flip."""
        sq_h, sq_w = 3, 6
        start, end = (5, 2), (4, 3) 
        
        # In RED perspective, (5,2) is "below-left" of (4,3).
        # Nearest corner is Bottom-Left: inner_r=2, inner_c=0.
        r_sub, c_sub = get_hotkey_subpos(start, end, 'R', sq_h, sq_w)
        self.assertEqual((r_sub, c_sub), (2, 0))
        
        # In BLACK perspective, (5,2) is "above-right" of (4,3).
        # Nearest corner is Top-Right: inner_r=0, inner_c=5.
        r_sub, c_sub = get_hotkey_subpos(start, end, 'B', sq_h, sq_w)
        self.assertEqual((r_sub, c_sub), (0, 5))

    def test_initial_board_setup(self):
        """Standard board should have 12 pieces for each side."""
        grid = setup_board()
        reds = sum(1 for r in grid for p in r if p and p.color == 'R')
        blacks = sum(1 for r in grid for p in r if p and p.color == 'B')
        self.assertEqual(reds, 12)
        self.assertEqual(blacks, 12)

    def test_piece_slide_forward(self):
        """A normal piece should move diagonally forward into empty space."""
        grid = empty_grid()
        grid[5][2] = Piece('R')
        state = create_mock_state(grid, 'R')
        
        # Test move calculation
        jumps, slides = get_piece_moves(state.grid, (5, 2))
        self.assertIn(((5, 2), (4, 1)), slides)
        self.assertIn(((5, 2), (4, 3)), slides)
        self.assertEqual(len(jumps), 0)

    def test_single_jump_capture(self):
        """A piece should be able to jump over and capture an opponent."""
        grid = empty_grid()
        grid[5][2] = Piece('R')
        grid[4][3] = Piece('B') # Opponent to jump
        state = create_mock_state(grid, 'R')
        
        jumps, slides = get_piece_moves(state.grid, (5, 2))
        expected_jump = ((5, 2), (3, 4), (4, 3))
        self.assertIn(expected_jump, jumps)
        
        # Execute the jump
        new_state = execute_move(state, expected_jump)
        self.assertIsNone(new_state.grid[5][2]) # Old pos empty
        self.assertIsNone(new_state.grid[4][3]) # Captured piece removed
        self.assertEqual(new_state.grid[3][4].color, 'R') # Landed safely

    def test_kinging_at_opposite_end(self):
        """A normal piece reaching the final row should be promoted to King."""
        grid = empty_grid()
        grid[1][2] = Piece('R') # One step away from top row
        state = create_mock_state(grid, 'R')
        
        move = ((1, 2), (0, 3))
        new_state = execute_move(state, move)
        landed_piece = new_state.grid[0][3]
        self.assertTrue(landed_piece.is_king)

    def test_forced_double_jump(self):
        """If a piece has another jump available, its turn must continue."""
        grid = empty_grid()
        grid[5][2] = Piece('R')
        grid[4][3] = Piece('B')
        grid[2][5] = Piece('B')
        state = create_mock_state(grid, 'R')
        
        # Manually trigger hotkeys for the mock state
        available = [((5, 2), (3, 4), (4, 3))]
        state = replace(state, hotkeys={ '1': available[0] })
        
        next_state = execute_move(state, available[0])
        
        # Should still be RED's turn and have a current_jumper set
        self.assertEqual(next_state.turn, 'R')
        self.assertEqual(next_state.current_jumper, (3, 4))
        # Check that the next jump is in hotkeys
        self.assertIn((3, 4), list(next_state.hotkeys.values())[0])

if __name__ == "__main__":
    unittest.main()
