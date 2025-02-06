from chess.board import Board

class Rules:
    @staticmethod
    def is_check(board, king_position, color):
        """Check if the king of the given color is in check."""
        row, col = king_position
        # Check all directions for pieces that could attack the king
        for r in range(8):
            for c in range(8):
                piece = board.board[r][c]
                if piece and piece.color != color:
                    if (row, col) in piece.valid_moves((r, c), board.board):
                        return True
        return False

    @staticmethod
    def is_checkmate(board, king_position, color):
        """Check if the king of the given color is in checkmate."""
        # Check if the king is in check
        if not Rules.is_check(board, king_position, color):
            return False
        
        # Check if the king can escape the check
        row, col = king_position
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board.board[r][c]
                if piece is None or piece.color != color:
                    # Check if the king can move to the square and not be in check
                    if not Rules.is_check(board, (r, c), color):
                        return False

        # Check if any other piece can block the check or capture the attacking piece
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
        """Validate if a move is legal, ensuring the king does not remain in check."""
        
        start_pos, end_pos = board.notation_to_index(move)
        piece = board.get_piece(start_pos)

        if not piece or piece.color != color:
            return False  # No piece selected or wrong color

        valid_moves = piece.valid_moves(board, start_pos)

        if end_pos not in valid_moves:
            return False  # Move is not valid

        return True  # Move is valid



    @staticmethod
    def is_valid_move(start, end, board):
        """Validate if the move from start to end is legal for the piece at start."""
        start_row, start_col = start
        end_row, end_col = end
        piece = board.board[start_row][start_col]
        
        if piece is None:
            return False  # No piece to move
        
        valid_moves = piece.valid_moves((start_row, start_col), board.board)
        if (end_row, end_col) in valid_moves:
            target_piece = board.board[end_row][end_col]
            if target_piece is None or target_piece.color != piece.color:
                # Simulate the move
                temp_board = Board()
                temp_board.board = [row[:] for row in board.board]
                temp_board.board[end_row][end_col] = temp_board.board[start_row][start_col]
                temp_board.board[start_row][start_col] = None

                # Check if the move puts the king in check
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
    def is_king_in_check(board, color):
        # Locate the king's position
        king_pos = board.find_king(color)
        
        # Check if any opponent piece can attack the king's position
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
            # Simulate the move
            original_piece = board.board[move[0]][move[1]]
            board.board[move[0]][move[1]] = board.board[move[0]][move[1]]  # move the piece
            board.board[move[0]][move[1]] = None  # clear the start position
            if not Rules.is_king_in_check(board, color):
                valid_moves.append(move)
            # Undo the move
            board.board[move[0]][move[1]] = original_piece
        return valid_moves

