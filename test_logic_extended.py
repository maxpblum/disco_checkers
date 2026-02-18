"""Extended unit tests for Disco Checkers core logic."""
import unittest
from dataclasses import replace
from logic import setup_board, execute_move, is_valid_pos, get_piece_moves, get_all_available_moves, process_event, calculate_hotkeys
from models import Piece, GameState

def create_mock_state(grid, turn='R', running=True, winner=None):
    """Helper to construct a GameState with minimal boilerplate."""
    return GameState(
        grid=tuple(tuple(row) for row in grid),
        turn=turn,
        p1_type='human',
        p2_type='cpu',
        hotkeys={},
        running=running,
        winner=winner
    )

def empty_grid():
    """Helper to return an empty 8x8 checker board grid."""
    return [[None for _ in range(8)] for _ in range(8)]

class TestLogicExtended(unittest.TestCase):

    def test_is_valid_pos(self):
        """Test boundary checks for board positions."""
        self.assertTrue(is_valid_pos((0, 0)))
        self.assertTrue(is_valid_pos((7, 7)))
        self.assertFalse(is_valid_pos((-1, 0)))
        self.assertFalse(is_valid_pos((0, -1)))
        self.assertFalse(is_valid_pos((8, 0)))
        self.assertFalse(is_valid_pos((0, 8)))

    def test_king_movement(self):
        """Kings should be able to move and jump backwards."""
        grid = empty_grid()
        # Place a Red King in the middle
        grid[4][3] = Piece('R', is_king=True)
        # Place enemies around
        grid[3][2] = Piece('B') # Backward Left (relative to Red)
        grid[3][4] = Piece('B') # Backward Right
        grid[5][2] = Piece('B') # Forward Left
        grid[5][4] = Piece('B') # Forward Right
        
        state = create_mock_state(grid, 'R')
        jumps, moves = get_piece_moves(state.grid, (4, 3))
        
        # Should be able to jump all 4 directions
        self.assertEqual(len(jumps), 4)
        destinations = [j[1] for j in jumps]
        self.assertIn((2, 1), destinations) # Jump Backward Left
        self.assertIn((2, 5), destinations) # Jump Backward Right
        self.assertIn((6, 1), destinations) # Jump Forward Left
        self.assertIn((6, 5), destinations) # Jump Forward Right

    def test_forced_jumps(self):
        """If a jump is available, slides should not be valid moves."""
        grid = empty_grid()
        grid[5][2] = Piece('R')
        grid[4][3] = Piece('B') # Capture available
        # Also have an empty space to slide to
        # (5,2) -> (4,1) is a valid slide if no jump existed
        
        state = create_mock_state(grid, 'R')
        all_moves = get_all_available_moves(state.grid, 'R', None)
        
        # Check that only the jump is returned
        for move in all_moves:
            self.assertEqual(len(move), 3, "Only jumps (len 3) should be allowed")
            self.assertEqual(move[0], (5, 2))
            self.assertEqual(move[1], (3, 4))

    def test_double_jump_chain(self):
        """Completing a jump that enables another jump should keep the turn."""
        grid = empty_grid()
        grid[6][1] = Piece('R')
        grid[5][2] = Piece('B') # First victim
        grid[3][4] = Piece('B') # Second victim
        
        state = create_mock_state(grid, 'R')
        
        # 1. Execute first jump: (6,1) -> (4,3)
        jump1 = ((6, 1), (4, 3), (5, 2))
        state = execute_move(state, jump1)
        
        # State should still be 'R's turn
        self.assertEqual(state.turn, 'R')
        self.assertEqual(state.current_jumper, (4, 3))
        
        # Hotkeys should only contain the next jump
        self.assertEqual(len(state.hotkeys), 1)
        next_jump = list(state.hotkeys.values())[0]
        self.assertEqual(next_jump, ((4, 3), (2, 5), (3, 4)))
        
        # 2. Execute second jump
        state = execute_move(state, next_jump)
        
        # Turn should now end
        self.assertEqual(state.turn, 'B')
        self.assertIsNone(state.current_jumper)

    def test_win_condition(self):
        """Game should end when opponent has no pieces."""
        grid = empty_grid()
        grid[0][0] = Piece('R')
        # No Black pieces
        
        state = create_mock_state(grid, 'R')
        
        # Red makes a move (doesn't really matter where, just to trigger next turn check)
        # Actually, execute_move checks if the *next* player has moves.
        # So if R moves, it checks B. B has no pieces, so R wins.
        # We need a valid move for R to trigger the check.
        grid[1][1] = Piece('R')
        grid[2][2] = None
        
        # Fake move: (1,1) -> (2,2)
        move = ((1, 1), (2, 2))
        
        # We need to manually construct the state such that execute_move runs correctly.
        # `execute_move` expects the move to be valid for the piece in `state.grid`.
        state = create_mock_state(grid, 'R')
        
        # Execute move
        new_state = execute_move(state, move)
        
        self.assertEqual(new_state.winner, 'R')

    def test_process_event_tick(self):
        """Tick event should update time and handle CPU thinking."""
        grid = empty_grid()
        grid[5][2] = Piece('R')
        grid[4][1] = Piece('B') # R can jump
        
        # CPU is Red
        state = create_mock_state(grid, 'R')
        state = replace(state, p1_type='cpu')
        
        # 1. First tick sets think start time
        state = process_event(state, "tick", 100.0)
        self.assertEqual(state.cpu_think_start, 100.0)
        
        # 2. Short tick (less than 1s) does nothing
        state = process_event(state, "tick", 100.5)
        self.assertEqual(state.turn, 'R') # Still Red's turn
        
        # 3. Long tick triggers move
        # We need to ensure hotkeys are calculated for CPU
        state = replace(state, hotkeys=calculate_hotkeys(get_all_available_moves(state.grid, 'R', None)))
        
        state = process_event(state, "tick", 101.5)
        self.assertEqual(state.turn, 'B') # Turn passed to Black

    def test_process_event_key_quit(self):
        """Pressing 'q' should stop the game."""
        state = create_mock_state(empty_grid())
        state = process_event(state, "key", 'q')
        self.assertFalse(state.running)

if __name__ == "__main__":
    unittest.main()
