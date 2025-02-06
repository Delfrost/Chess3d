from chess.pieces import King

def find_king(board, color):
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if isinstance(piece, King) and piece.color == color:
                return row, col
    return None  # King not found (should never happen if the board is set up correctly)
