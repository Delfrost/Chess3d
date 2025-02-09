import pygame

class Piece:
    def __init__(self, color):
        self.color = color

    def valid_moves(self, pos, board):
        raise NotImplementedError

    def capture_moves(self, pos, board):
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def valid_moves(self, pos, board):
        row, col = pos
        direction = -1 if self.color == "white" else 1
        moves = []

        if 0 <= row + direction < 8 and board.board[row + direction][col] is None:
            moves.append((row + direction, col))

        if not self.has_moved and row == (6 if self.color == "white" else 1):
            if board.board[row + direction][col] is None and board.board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        for dc in [-1, 1]:
            if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                target = board.board[row + direction][col + dc]
                if target and target.color != self.color:
                    moves.append((row + direction, col + dc))

        return moves

    def move(self, start, end, board):
        self.has_moved = True

class Rook(Piece):
    def valid_moves(self, pos, board):
        row, col = pos
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row, col
            while 0 <= r + dr < 8 and 0 <= c + dc < 8:
                r, c = r + dr, c + dc
                if board.board[r][c] is None:
                    moves.append((r, c))
                elif board.board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

class Knight(Piece):
    def valid_moves(self, pos, board):
        row, col = pos
        moves = []
        for dr, dc in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.board[r][c]
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves

class Bishop(Piece):
    def valid_moves(self, pos, board):
        row, col = pos
        moves = []
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = row, col
            while 0 <= r + dr < 8 and 0 <= c + dc < 8:
                r, c = r + dr, c + dc
                if board.board[r][c] is None:
                    moves.append((r, c))
                elif board.board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

class Queen(Piece):
    def valid_moves(self, pos, board):
        row, col = pos
        moves = []
        for piece in [Rook(self.color), Bishop(self.color)]:
            moves.extend(piece.valid_moves(pos, board))
        return moves

class King(Piece):
    def valid_moves(self, position, board):
        row, col = position
        moves = []

        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),         (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        from chess.rules import Rules  

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board.board[new_row][new_col]

                if piece is None or piece.color != self.color:
                    original_piece = board.board[new_row][new_col]
                    board.board[new_row][new_col] = self
                    board.board[row][col] = None

                    if not getattr(board, "checking_king", False):  
                        board.checking_king = True
                        if not Rules.is_king_in_check(board, self.color):
                            moves.append((new_row, new_col))
                        board.checking_king = False
                    else:
                        moves.append((new_row, new_col))

                    board.board[row][col] = self
                    board.board[new_row][new_col] = original_piece

        return moves
