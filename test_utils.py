"""Unit tests for the ANSI-aware string utilities."""
import unittest
from utils import strip_ansi, visible_len, ansi_center, ansi_ljust, ansi_truncate

class TestUtils(unittest.TestCase):
    
    def test_strip_ansi(self):
        """Should remove all ANSI color codes from a string."""
        colored = "\033[91mHello\033[0m"
        self.assertEqual(strip_ansi(colored), "Hello")

    def test_visible_len(self):
        """Should count emojis as width 2 and normal chars as 1."""
        colored = "\033[91m🔴\033[0m VS \033[30m⚫\033[0m"
        # "🔴 VS ⚫"
        # 2 + 1( ) + 1(V) + 1(S) + 1( ) + 2 = 8
        self.assertEqual(visible_len(colored), 8)

    def test_ansi_center(self):
        """Should center colored text within a given width correctly."""
        colored = "\033[91mHI\033[0m" # Length 2
        width = 10
        centered = ansi_center(colored, width)
        
        # Strip ANSI to check visible centering
        visible_centered = strip_ansi(centered)
        self.assertEqual(len(visible_centered), 10)
        self.assertEqual(visible_centered, "    HI    ")
        
    def test_ansi_ljust(self):
        """Should left-justify colored text within a given width correctly."""
        colored = "\033[30mB\033[0m" # Length 1
        width = 4
        justified = ansi_ljust(colored, width)
        
        visible_justified = strip_ansi(justified)
        self.assertEqual(len(visible_justified), 4)
        self.assertEqual(visible_justified, "B   ")

    def test_ansi_truncate(self):
        """Should truncate string to visible width, preserving colors where possible."""
        colored = "\033[91mHello World\033[0m"
        truncated = ansi_truncate(colored, 5)
        # Should be "\033[91mHello"
        # Note: Depending on implementation, it might not include the reset code if it was after the truncation point.
        self.assertEqual(strip_ansi(truncated), "Hello")
        self.assertTrue(truncated.startswith("\033[91m"))
        
        # Test with emoji (width 2)
        emoji_str = "A🔴B"
        # Truncate at 2. "A" (1) + "🔴" (2) = 3. So it should only return "A".
        trunc_emoji = ansi_truncate(emoji_str, 2)
        self.assertEqual(trunc_emoji, "A")
        
        # Truncate at 3. Should return "A🔴"
        trunc_emoji_3 = ansi_truncate(emoji_str, 3)
        self.assertEqual(trunc_emoji_3, "A🔴")

if __name__ == "__main__":
    unittest.main()
