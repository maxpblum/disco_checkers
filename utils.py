"""Utility functions for ANSI-aware string manipulation."""
import re

ANSI_ESCAPE = re.compile(r'\033\[[0-9;]*[mK]')

def strip_ansi(text: str) -> str:
    """Removes ANSI escape sequences from a string to get visible content."""
    return ANSI_ESCAPE.sub('', text)

def char_width(char: str) -> int:
    """Returns the visible column width of a single character."""
    # Emojis and certain Unicode blocks take 2 cells
    if ord(char) > 0x1100:
        return 2
    return 1

def visible_len(text: str) -> int:
    """Returns the total visible column width of a string."""
    clean = strip_ansi(text)
    return sum(char_width(c) for c in clean)

def ansi_truncate(text: str, width: int) -> str:
    """Safely truncates a string with ANSI codes to a specific visible width."""
    result = ""
    current_vlen = 0
    parts = re.split(r'(\033\[[0-9;]*[mK])', text)
    for part in parts:
        if part.startswith('\033['):
            result += part
        else:
            for char in part:
                w = char_width(char)
                if current_vlen + w <= width:
                    result += char
                    current_vlen += w
                else:
                    return result
    return result

def ansi_center(text: str, width: int) -> str:
    """Centers a string within a given width, accounting for character widths."""
    vlen = visible_len(text)
    if vlen >= width:
        return ansi_truncate(text, width)
    left_pad = (width - vlen) // 2
    right_pad = width - vlen - left_pad
    return (" " * left_pad) + text + (" " * right_pad)

def ansi_ljust(text: str, width: int) -> str:
    """Left-justifies a string within a given width, accounting for character widths."""
    vlen = visible_len(text)
    if vlen >= width:
        return ansi_truncate(text, width)
    return text + (" " * (width - vlen))
