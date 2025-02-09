from chess.pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]

    def reset(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup()

    def setup(self):
        for col in range(8):
            self.board[1][col] = Pawn("black")
            self.board[6][col] = Pawn("white")

        self.board[0][0] = Rook("black")
        self.board[0][7] = Rook("black")
        self.board[7][0] = Rook("white")
        self.board[7][7] = Rook("white")

        self.board[0][1] = Knight("black")
        self.board[0][6] = Knight("black")
        self.board[7][1] = Knight("white")
        self.board[7][6] = Knight("white")

        self.board[0][2] = Bishop("black")
        self.board[0][5] = Bishop("black")
        self.board[7][2] = Bishop("white")
        self.board[7][5] = Bishop("white")

        self.board[0][3] = Queen("black")
        self.board[7][3] = Queen("white")

        self.board[0][4] = King("black")
        self.board[7][4] = King("white")

    def display(self):
        for row in self.board:
            print(" ".join([f"{piece.__class__.__name__[0]}({piece.color[0]})" if piece else "." for piece in row]))

    def apply_move(self, move):
        start, end = move.split()
        start_row, start_col = self._convert_position(start)
        end_row, end_col = self._convert_position(end)

        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = None

    def _convert_position(self, pos):
        col = ord(pos[0].lower()) - ord('a')
        row = 8 - int(pos[1])
        return row, col

    def get_piece(self, position):
        row, col = position
        return self.board[row][col]

    def move_piece(self, start, end):
        piece = self.board[start[0]][start[1]]
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = None

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None
