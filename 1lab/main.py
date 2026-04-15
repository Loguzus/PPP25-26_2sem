import sys
def to_coords(notation):
    try:
        if len(notation) != 2: return None
        col = ord(notation[0].lower()) - ord('a')
        row = 8 - int(notation[1])
        if 0 <= col < 8 and 0 <= row < 8:
            return row, col
        return None
    except:
        return None
class Move:
    def __init__(self, piece, start, end, captured=None, cap_pos=None):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured = captured
        self.cap_pos = cap_pos if cap_pos else end
class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
    def display(self):
        print("\n    a b c d e f g h")
        print("  +-----------------+")
        for r in range(8):
            line = f"{8 - r} | "
            for c in range(8):
                p = self.grid[r][c]
                line += (p.symbol if p else ".") + " "
            print(line + f"| {8 - r}")
        print("  +-----------------+")
        print("    a b c d e f g h\n")
class Piece:
    def __init__(self, color, symbol):
        self.color = color
        self.symbol = symbol
    def get_valid_moves(self, board, pos):
        return []
class ChessPawn(Piece):
    def __init__(self, color):
        super().__init__(color, '♟' if color == 'White' else '♙')
    def get_valid_moves(self, board, pos):
        moves = []
        r, c = pos
        d = -1 if self.color == 'White' else 1
        if 0 <= r + d < 8 and board.grid[r + d][c] is None:
            moves.append(Move(self, pos, (r + d, c)))
            start_r = 6 if self.color == 'White' else 1
            if r == start_r and board.grid[r + d][c] is None and board.grid[r + 2 * d][c] is None:
                moves.append(Move(self, pos, (r + 2 * d, c)))
        for dc in [-1, 1]:
            nr, nc = r + d, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target and target.color != self.color:
                    moves.append(Move(self, pos, (nr, nc), target))
        return moves
class SlidingPiece(Piece):
    def get_moves(self, board, pos, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = pos[0] + dr, pos[1] + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target is None:
                    moves.append(Move(self, pos, (nr, nc)))
                elif target.color != self.color:
                    moves.append(Move(self, pos, (nr, nc), target))
                    break
                else:
                    break
                nr, nc = nr + dr, nc + dc
        return moves
class ChessKnight(Piece):
    def __init__(self, color):
        super().__init__(color, '♞' if color == 'White' else '♘')
    def get_valid_moves(self, board, pos):
        moves = []
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target is None or target.color != self.color:
                    moves.append(Move(self, pos, (nr, nc), target))
        return moves
class ChessRook(SlidingPiece):
    def __init__(self, color): super().__init__(color, '♜' if color == 'White' else '♖')

    def get_valid_moves(self, b, p): return self.get_moves(b, p, [(0, 1), (0, -1), (1, 0), (-1, 0)])
class ChessBishop(SlidingPiece):
    def __init__(self, color): super().__init__(color, '♝' if color == 'White' else '♗')

    def get_valid_moves(self, b, p): return self.get_moves(b, p, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
class ChessQueen(SlidingPiece):
    def __init__(self, color): super().__init__(color, '♛' if color == 'White' else '♕')
    def get_valid_moves(self, b, p): return self.get_moves(b, p,
                                                           [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1),
                                                            (-1, -1)])
class ChessKing(Piece):
    def __init__(self, color):
        super().__init__(color, '♚' if color == 'White' else '♔')
    def get_valid_moves(self, board, pos):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = pos[0] + dr, pos[1] + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board.grid[nr][nc]
                    if target is None or target.color != self.color:
                        moves.append(Move(self, pos, (nr, nc), target))
        return moves
class CheckerPiece(Piece):
    def __init__(self, color):
        super().__init__(color, '●' if color == 'White' else '○')
    def get_valid_moves(self, board, pos):
        moves = []
        r, c = pos
        # Белые шашки ходят вверх (-1)
        d = -1 if self.color == 'White' else 1
        for dc in [-1, 1]:
            # Обычный ход по диагонали
            nr, nc = r + d, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board.grid[nr][nc] is None:
                    moves.append(Move(self, pos, (nr, nc)))
                else:
                    # Прыжок через врага
                    jr, jc = nr + d, nc + dc
                    if 0 <= jr < 8 and 0 <= jc < 8:
                        if board.grid[nr][nc].color != self.color and board.grid[jr][jc] is None:
                            moves.append(Move(self, pos, (jr, jc), board.grid[nr][nc], (nr, nc)))
        return moves
class GameEngine:
    def __init__(self, mode='1'):
        self.board = Board()
        self.turn = 'White'
        self.history = []
        self.setup(mode)
    def setup(self, mode):
        if mode == '1':  # Шахматы
            order = [ChessRook, ChessKnight, ChessBishop, ChessQueen, ChessKing, ChessBishop, ChessKnight, ChessRook]
            for i, cls in enumerate(order):
                self.board.grid[0][i] = cls('Black')
                self.board.grid[7][i] = cls('White')
                self.board.grid[1][i] = ChessPawn('Black')
                self.board.grid[6][i] = ChessPawn('White')
        else:  # Шашки
            for r in range(3):  # Черные сверху
                for c in range(8):
                    if (r + c) % 2 != 0: self.board.grid[r][c] = CheckerPiece('Black')
            for r in range(5, 8):  # Белые снизу
                for c in range(8):
                    if (r + c) % 2 != 0: self.board.grid[r][c] = CheckerPiece('White')
    def play(self):
        print(f"Игра началась! Ход {self.turn}. Формат: a2 a4; undo; exit")
        while True:
            self.board.display()
            inp = input(f"Ход ({self.turn}): ").strip().lower().split()
            if not inp: continue
            if inp[0] == 'exit': break
            if inp[0] == 'undo' and self.history:
                m = self.history.pop()
                self.board.grid[m.start[0]][m.start[1]] = m.piece
                self.board.grid[m.end[0]][m.end[1]] = None
                if m.captured: self.board.grid[m.cap_pos[0]][m.cap_pos[1]] = m.captured
                self.turn = 'Black' if self.turn == 'White' else 'White'
                continue
            if len(inp) == 2:
                s_coords, e_coords = to_coords(inp[0]), to_coords(inp[1])
                if s_coords and e_coords:
                    p = self.board.grid[s_coords[0]][s_coords[1]]
                    if p and p.color == self.turn:
                        valid = p.get_valid_moves(self.board, s_coords)
                        move = next((m for m in valid if m.end == e_coords), None)
                        if move:
                            self.board.grid[s_coords[0]][s_coords[1]] = None
                            if move.captured: self.board.grid[move.cap_pos[0]][move.cap_pos[1]] = None
                            self.board.grid[e_coords[0]][e_coords[1]] = p
                            self.history.append(move)
                            self.turn = 'Black' if self.turn == 'White' else 'White'
                            continue
            print("!!! Ошибка: Некорректный ход или не ваша фигура.")
if __name__ == "__main__":
    m = input("Выберите игру (1 - Шахматы, 2 - Шашки): ")
    GameEngine(m).play()
