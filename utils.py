"""
Utility functions for ANSI-aware string manipulation.

These helpers correctly handle strings containing ANSI escape codes (colors, styles),
ensuring that layout calculations (width, centering, truncation) are based on the
*visible* content rather than the raw byte length.
"""
import re

# Regex to identify ANSI escape sequences (e.g., \033[31m)
ANSI_ESCAPE = re.compile(r'\033\[[0-9;]*[mK]')

def strip_ansi(text: str) -> str:
    """
    Removes ANSI escape sequences from a string to get visible content.

    Args:
        text (str): The string with potential ANSI codes.

    Returns:
        str: The plain text string.
    """
    return ANSI_ESCAPE.sub('', text)

def char_width(char: str) -> int:
    """
    Returns the visible column width of a single character.

    Args:
        char (str): A single character string.

    Returns:
        int: 2 for wide characters (e.g., emojis), 1 for others.
    """
    # Simple heuristic: Characters above U+1100 (Hangul, Emojis, CJK) are usually wide.
    if ord(char) > 0x1100:
        return 2
    return 1

def visible_len(text: str) -> int:
    """
    Returns the total visible column width of a string.

    Args:
        text (str): The string to measure.

    Returns:
        int: The sum of visible widths of its characters (ignoring ANSI codes).
    """
    clean = strip_ansi(text)
    return sum(char_width(c) for c in clean)

def ansi_truncate(text: str, width: int) -> str:
    """
    Safely truncates a string with ANSI codes to a specific visible width.

    Preserves ANSI codes as much as possible while cutting off visible text
    that exceeds the width.

    Args:
        text (str): The string to truncate.
        width (int): The maximum visible width.

    Returns:
        str: The truncated string, possibly ending with an ANSI reset (implicit).
    """
    result = ""
    current_vlen = 0
    # Split by ANSI codes to process text chunks and codes separately
    parts = re.split(r'(\033\[[0-9;]*[mK])', text)
    
    for part in parts:
        if part.startswith('\033['):
            # Always append ANSI codes (they have 0 width)
            result += part
        else:
            # Iterate through visible characters
            for char in part:
                w = char_width(char)
                if current_vlen + w <= width:
                    result += char
                    current_vlen += w
                else:
                    return result
    return result

def ansi_center(text: str, width: int) -> str:
    """
    Centers a string within a given width, accounting for character widths and ANSI codes.

    Args:
        text (str): The string to center.
        width (int): The total width of the resulting string.

    Returns:
        str: The centered string with padding.
    """
    vlen = visible_len(text)
    if vlen >= width:
        return ansi_truncate(text, width)
    
    left_pad = (width - vlen) // 2
    right_pad = width - vlen - left_pad
    return (" " * left_pad) + text + (" " * right_pad)

def ansi_ljust(text: str, width: int) -> str:
    """
    Left-justifies a string within a given width, accounting for character widths and ANSI codes.

    Args:
        text (str): The string to justify.
        width (int): The total width of the resulting string.

    Returns:
        str: The padded string.
    """
    vlen = visible_len(text)
    if vlen >= width:
        return ansi_truncate(text, width)
    
    return text + (" " * (width - vlen))
