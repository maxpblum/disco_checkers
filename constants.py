"""Constants for colors, ASCII art, and game settings."""

class Colors:
    """ANSI color escape sequences."""
    RED_FG = "\033[91m"
    BLACK_FG = "\033[30m"
    GRAY_LIGHT = "\033[47m"
    GRAY_DARK = "\033[100m"
    YELLOW_BG = "\033[43m"
    YELLOW_FG = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    WHITE_FG = "\033[97m"
    MAGENTA_FG = "\033[95m"
    CYAN_FG = "\033[96m"
    GREEN_FG = "\033[92m"
    GREEN_BG = "\033[42m"

SPARKLES_FG = [
    Colors.RED_FG, 
    Colors.MAGENTA_FG, 
    Colors.CYAN_FG, 
    Colors.GREEN_FG, 
    Colors.WHITE_FG
]

POSSIBLE_KEYS = "123456789abcdefghijklmnoprstuvwxyz"

ASCII_DISCO = [
    " ___  ___ ___  ___  ___     ___ _  _ ___ ___ _  _ ___ ___ ___ ",
    "|   \|_ _/ __|/ __|/ _ \   / __| || | __/ __| |/ | __| _ \ __|",
    "| |) || |\__ \ (__| (_) | | (__| __ | _| (__| ' <| _|   / _| ",
    "|___/|___|___/\___|\___/   \___|_||_|___\___|_|\_\___|_|_\___|"
]
