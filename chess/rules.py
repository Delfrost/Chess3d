from chess.board import Board
from chess.pieces import Rook, Bishop, Queen, King, Knight, Pawn

class Rules:

    @staticmethod
    def is_check(board, king_position, color):
        row, col = king_position
        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]
                if piece and piece.color != color:
                    if (row, col) in piece.valid_moves((r, c), board):
                        return True
        return False

    @staticmethod
    def is_checkmate(board, king_position, color):
        if not Rules.is_check(board, king_position, color):
            return False
        
        row, col = king_position
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board.board[r][c]
                if piece is None or piece.color != color:
                    if not Rules.is_check(board, (r, c), color):
                        return False

        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]
                if piece and piece.color == color:
                    valid_moves = piece.valid_moves((r, c), board.board)
                    for move in valid_moves:
                        temp_board = Board()
                        temp_board.board = [row[:] for row in board.board]
                        temp_board.board[move[0]][move[1]] = temp_board.board[r][c]
                        temp_board.board[r][c] = None
                        if not Rules.is_check(temp_board, king_position, color):
                            return False

        return True

    @staticmethod
    def validate_move(board, move, color):
        start_pos, end_pos = board.notation_to_index(move)
        piece = board.get_piece(start_pos)

        if not piece or piece.color != color:
            return False

        valid_moves = piece.valid_moves(board, start_pos)

        if end_pos not in valid_moves:
            return False

        return True

    @staticmethod
    def is_king_in_check(board, color):
        king_pos = board.find_king(color)
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color != color:
                    if king_pos in piece.valid_moves((row, col), board):
                        return True
        return False

    @staticmethod
    def filter_moves_that_leave_king_in_check(board, color, moves):
        valid_moves = []
        for move in moves:
            original_piece = board.board[move[0]][move[1]]
            board.board[move[0]][move[1]] = board.board[move[0]][move[1]]
            board.board[move[0]][move[1]] = None
            if not Rules.is_king_in_check(board, color):
                valid_moves.append(move)
            board.board[move[0]][move[1]] = original_piece
        return valid_moves
    
    @staticmethod
    def is_valid_move(start, end, board, color):
        start_row, start_col = start
        end_row, end_col = end
        piece = board.board[start_row][start_col]
        
        if piece is None:
            return False

        if Rules.is_king_in_check(board, color):
            if not (Rules.is_checkmate(board, (start_row, start_col), color) or 
                    piece.__class__.__name__.lower() == 'king' or 
                    Rules.can_block_or_capture_check(start_row, start_col, piece, end_row, end_col, board)):
                return False

        valid_moves = piece.valid_moves((start_row, start_col), board.board)
        if (end_row, end_col) in valid_moves:
            target_piece = board.board[end_row][end_col]
            if target_piece is None or target_piece.color != piece.color:
                temp_board = Board()
                temp_board.board = [row[:] for row in board.board]
                temp_board.board[end_row][end_col] = temp_board.board[start_row][start_col]
                temp_board.board[start_row][start_col] = None

                king_position = None
                for r in range(8):
                    for c in range(8):
                        temp_piece = temp_board.board[r][c]
                        if temp_piece and temp_piece.__class__.__name__.lower() == 'king' and temp_piece.color == piece.color:
                            king_position = (r, c)
                            break

                if not king_position:
                    return False

                if Rules.is_check(temp_board, king_position, piece.color):
                    return False

                return True
        return False

    @staticmethod
    def can_block_or_capture_check(start_row, start_col, piece, end_row, end_col, board):
        king_pos = None
        for r in range(8):
            for c in range(8):
                temp_piece = board.board[r][c]
                if temp_piece and temp_piece.__class__.__name__.lower() == 'king' and temp_piece.color == piece.color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        check_row, check_col = Rules.get_checking_piece_position(board, king_pos, piece.color)

        if check_row is None and check_col is None:
            return False

        if piece.__class__.__name__.lower() in ['rook', 'bishop', 'queen']:
            return Rules.can_block_check_with_line_piece(start_row, start_col, piece, check_row, check_col, board)
        if piece.__class__.__name__.lower() == 'king':
            return Rules.can_capture_checking_piece(start_row, start_col, piece, check_row, check_col, board)
        
        return False

    @staticmethod
    def can_block_check_with_line_piece(start_row, start_col, piece, check_row, check_col, board):
        if isinstance(piece, (Rook, Queen)):
            if start_col == check_col:
                return Rules.is_between_check_and_king(start_row, start_col, check_row, check_col, board)
            elif start_row == check_row:
                return Rules.is_between_check_and_king(start_row, start_col, check_row, check_col, board)
        elif isinstance(piece, Bishop):
            if abs(start_row - check_row) == abs(start_col - check_col):
                return Rules.is_between_check_and_king(start_row, start_col, check_row, check_col, board)
        return False

    @staticmethod
    def can_capture_checking_piece(start_row, start_col, piece, check_row, check_col, board):
        if isinstance(piece, King):
            if abs(start_row - check_row) <= 1 and abs(start_col - check_col) <= 1:
                target_piece = board.board[check_row][check_col]
                if target_piece and target_piece.color != piece.color:
                    return True
        return False

    @staticmethod
    def is_between_check_and_king(start_row, start_col, check_row, check_col, board):
        if start_row == check_row:
            if start_col > check_col:
                for c in range(check_col + 1, start_col):
                    if board.board[start_row][c] is not None:
                        return False
            else:
                for c in range(start_col + 1, check_col):
                    if board.board[start_row][c] is not None:
                        return False
        elif start_col == check_col:
            if start_row > check_row:
                for r in range(check_row + 1, start_row):
                    if board.board[r][start_col] is not None:
                        return False
            else:
                for r in range(start_row + 1, check_row):
                    if board.board[r][start_col] is not None:
                        return False
        elif abs(start_row - check_row) == abs(start_col - check_col):
            row_step = 1 if check_row > start_row else -1
            col_step = 1 if check_col > start_col else -1
            r, c = start_row + row_step, start_col + col_step
            while (r != check_row) and (c != check_col):
                if board.board[r][c] is not None:
                    return False
                r += row_step
                c += col_step
        return True

    @staticmethod
    def get_checking_piece_position(board, king_pos, color):
        check_row, check_col = None, None
        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]
                if piece and piece.color != color:
                    if isinstance(piece, (Rook, Bishop, Queen)):
                        if Rules.is_attack_possible(piece, r, c, king_pos[0], king_pos[1], board):
                            check_row, check_col = r, c
                            break
                    elif isinstance(piece, Knight):
                        if Rules.is_knight_check(piece, r, c, king_pos[0], king_pos[1]):
                            check_row, check_col = r, c
                            break
                    elif isinstance(piece, King):
                        if abs(r - king_pos[0]) <= 1 and abs(c - king_pos[1]) <= 1:
                            check_row, check_col = r, c
                            break
                    elif isinstance(piece, Pawn):
                        if Rules.is_pawn_check(piece, r, c, king_pos[0], king_pos[1]):
                            check_row, check_col = r, c
                            break
        return check_row, check_col
