import random
import time
import os
import sys
import tty
import termios
import select

# ANSI Colors and Disco Effects
class Colors:
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BG_DARK = "\033[40m"
    BG_PURPLE = "\033[45m"
    BLINK = "\033[5m"

# Disco "Sparkle" effect
def get_sparkle():
    return random.choice([Colors.MAGENTA, Colors.CYAN, Colors.YELLOW, Colors.GREEN])

class Piece:
    def __init__(self, color, is_king=False):
        self.color = color # 'R' (Red/Magenta) or 'W' (White/Cyan)
        self.is_king = is_king

    def __str__(self):
        char = "K" if self.is_king else "O"
        color_code = Colors.MAGENTA if self.color == 'R' else Colors.CYAN
        if self.is_king:
            return f"{get_sparkle()}{Colors.BOLD}{char}{Colors.RESET}"
        return f"{color_code}{Colors.BOLD}{char}{Colors.RESET}"

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self._setup_pieces()

    def _setup_pieces(self):
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece('W')
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece('R')

    def draw(self, selected=None, last_move=None, hotkeys=None, status=""):
        now = time.time()
        try:
            term_size = os.get_terminal_size()
            term_w = term_size.columns
            term_h = term_size.lines
        except OSError:
            term_w, term_h = 80, 24

        sys.stdout.write("\033[?25l") # Hide cursor
        
        ui_h = 6 
        ui_w = 4
        max_sq_h = (term_h - ui_h) // 8
        max_sq_w = (term_w - ui_w) // 8
        sq_h = max(1, min(max_sq_h, max_sq_w // 2))
        sq_w = sq_h * 2

        buffer = []
        buffer.append("\033[H") # Home
        
        header = "DISCO CHECKERS"
        buffer.append(f"{Colors.YELLOW}{Colors.BOLD}{header.center(term_w)}{Colors.RESET}\r\n")
        
        col_labels = "  " + "".join([str(i).center(sq_w) for i in range(8)])
        buffer.append(f"{col_labels}\r\n")

        hotkey_lookup = {}
        if hotkeys:
            for key, move in hotkeys.items():
                dest = move[1]
                if dest not in hotkey_lookup:
                    hotkey_lookup[dest] = []
                hotkey_lookup[dest].append(key)

        sparkles = [Colors.MAGENTA, Colors.CYAN, Colors.YELLOW, Colors.GREEN, Colors.RED]

        for r in range(8):
            for inner_r in range(sq_h):
                row_str = f"{r} " if inner_r == sq_h // 2 else "  "
                for c in range(8):
                    bg = Colors.BG_DARK if (r + c) % 2 == 0 else Colors.BG_PURPLE
                    if selected == (r, c): bg = "\033[43m"
                    elif last_move and (r, c) in last_move: bg = "\033[42m"

                    piece = self.grid[r][c]
                    content = ""
                    cy, cx = (sq_h - 1) / 2.0, (sq_w - 1) / 2.0
                    
                    if (r, c) in hotkey_lookup and inner_r == sq_h // 2:
                        keys_str = "/".join(hotkey_lookup[(r, c)])[:sq_w]
                        pad_l = (sq_w - len(keys_str)) // 2
                        pad_r = sq_w - len(keys_str) - pad_l
                        content = (" " * pad_l) + f"{Colors.YELLOW}{Colors.BOLD}{keys_str}{Colors.RESET}{bg}" + (" " * pad_r)
                    elif piece:
                        color = sparkles[int(now * 6) % len(sparkles)] if piece.is_king else \
                                (Colors.MAGENTA if piece.color == 'R' else Colors.CYAN) if int(now * 2) % 2 == 0 else \
                                (Colors.RED if piece.color == 'R' else Colors.GREEN)
                            
                        for inner_c in range(sq_w):
                            dx, dy = inner_c - cx, (inner_r - cy) * 2.0 
                            dist = (dx*dx + dy*dy)**0.5
                            if dist < sq_h * 0.8:
                                is_k = piece.is_king and inner_r == sq_h // 2 and inner_c in [int(cx), int(cx+0.5)]
                                content += f"{color}{'K' if is_k else '█'}{Colors.RESET}{bg}"
                            else: content += " "
                    else: content = " " * sq_w
                    row_str += f"{bg}{content}{Colors.RESET}"
                buffer.append(row_str + "\r\n")
        
        footer = f"{Colors.YELLOW}{('-' * (sq_w * 8))}{Colors.RESET}"
        buffer.append(f"{footer.center(term_w)}\r\n")
        buffer.append(status.center(term_w) + "\r\n")
        
        sys.stdout.write("".join(buffer))
        sys.stdout.flush()

    def get_piece(self, pos):
        return self.grid[pos[0]][pos[1]]

    def set_piece(self, pos, piece):
        self.grid[pos[0]][pos[1]] = piece

    def move_piece(self, start, end):
        piece = self.get_piece(start)
        self.set_piece(start, None)
        self.set_piece(end, piece)
        
        # Kinging
        kinged = False
        if piece.color == 'R' and end[0] == 0 and not piece.is_king:
            piece.is_king = True
            kinged = True
        elif piece.color == 'W' and end[0] == 7 and not piece.is_king:
            piece.is_king = True
            kinged = True
        return kinged

    def is_valid_pos(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

class Game:
    def __init__(self, p1_type='human', p2_type='cpu'):
        self.board = Board()
        self.turn = 'R' # Red (Magenta) starts
        self.p1_type = p1_type
        self.p2_type = p2_type
        self.running = True

    def get_moves(self, color):
        jumps = []
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board.grid[r][c]
                if piece and piece.color == color:
                    p_jumps, p_moves = self.get_piece_moves((r, c))
                    jumps.extend(p_jumps)
                    moves.extend(p_moves)
        return jumps if jumps else moves

    def get_piece_moves(self, pos):
        r, c = pos
        piece = self.board.get_piece(pos)
        jumps = []
        moves = []

        dirs = []
        if piece.is_king:
            dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif piece.color == 'R':
            dirs = [(-1, -1), (-1, 1)]
        else: # White
            dirs = [(1, -1), (1, 1)]

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if self.board.is_valid_pos((nr, nc)):
                target = self.board.get_piece((nr, nc))
                if target is None:
                    moves.append((pos, (nr, nc)))
                elif target.color != piece.color:
                    jr, jc = nr + dr, nc + dc
                    if self.board.is_valid_pos((jr, jc)) and self.board.get_piece((jr, jc)) is None:
                        jumps.append((pos, (jr, jc), (nr, nc)))
        
        return jumps, moves

    def get_key_non_blocking(self):
        fd = sys.stdin.fileno()
        if select.select([sys.stdin], [], [], 0)[0]:
            try:
                return os.read(fd, 1).decode('utf-8')
            except:
                return None
        return None

    def play(self):
        current_jumper = None
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            # Enter alternate screen and raw mode
            sys.stdout.write("\033[?1049h\033[H")
            sys.stdout.flush()
            tty.setraw(fd)
            
            while self.running:
                if current_jumper:
                    moves, _ = self.get_piece_moves(current_jumper)
                    if not moves:
                        current_jumper = None
                        self.turn = 'W' if self.turn == 'R' else 'R'
                        continue
                else:
                    moves = self.get_moves(self.turn)
                
                if not moves:
                    self.board.draw(status="GAME OVER! Press any key to exit.")
                    while not self.get_key_non_blocking(): time.sleep(0.05)
                    break

                possible_keys = "123456789abcdefghijklmnoprstuvwxyz"
                hotkeys = {possible_keys[i]: moves[i] for i in range(min(len(moves), len(possible_keys)))}
                current_type = self.p1_type if self.turn == 'R' else self.p2_type
                
                move = None
                last_draw = 0
                cpu_think_start = time.time() if current_type == 'cpu' else None
                
                while not move:
                    now = time.time()
                    if now - last_draw > 0.05:
                        color_name = "MAGENTA" if self.turn == 'R' else "CYAN"
                        status_msg = f"Turn: {color_name} ({current_type.upper()}) | Press 'q' to Quit"
                        self.board.draw(hotkeys=hotkeys, status=status_msg)
                        last_draw = now

                    key = self.get_key_non_blocking()
                    if key == 'q':
                        self.running = False
                        return
                    
                    if current_type == 'human':
                        if key in hotkeys:
                            move = hotkeys[key]
                    else:
                        if now - cpu_think_start > 1.0:
                            move = self.get_cpu_move(moves)
                    time.sleep(0.01)
                
                # Execute move
                start, end = move[0], move[1]
                if len(move) == 3: # Jump
                    self.board.set_piece(move[2], None) # Remove captured
                    kinged = self.board.move_piece(start, end)
                    if not kinged:
                        jumps, _ = self.get_piece_moves(end)
                        if jumps:
                            current_jumper = end
                            continue
                else:
                    self.board.move_piece(start, end)

                current_jumper = None
                self.turn = 'W' if self.turn == 'R' else 'R'
        finally:
            # Exit alternate screen, show cursor, restore settings
            sys.stdout.write("\033[?1049l\033[?25h")
            sys.stdout.flush()
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_key(self):
        pass # Replaced by get_key_non_blocking

    def get_human_move(self, moves):
        pass # Replaced by integrated logic in play()

    def get_cpu_move(self, moves):
        # Basic CPU: pick a random jump if available, else a random move
        # (Already filtered to only jumps if any exist)
        return random.choice(moves)

if __name__ == "__main__":
    print(f"{Colors.BG_PURPLE}{Colors.YELLOW}{Colors.BOLD}   WELCOME TO DISCO CHECKERS   {Colors.RESET}")
    p1 = input("Player 1 (MAGENTA) - (h)uman or (c)pu? ").lower().startswith('h')
    p2 = input("Player 2 (CYAN)    - (h)uman or (c)pu? ").lower().startswith('h')
    
    game = Game(
        p1_type='human' if p1 else 'cpu',
        p2_type='human' if p2 else 'cpu'
    )
    game.play()
