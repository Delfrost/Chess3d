import pygame
from chess.board import Board
from chess.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from chess.rules import Rules  # Import Rules class to handle check/valid moves

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800  # Window dimensions
ROWS, COLS = 8, 8         # Chessboard grid
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (50, 205, 50, 128)  # Green with 50% opacity for regular moves
CAPTURE_COLOR = (255, 0, 0, 128)      # Red with 50% opacity for capture moves

# Piece type mapping by class
PIECE_TYPE_MAP = {
    Pawn: 'pawn',
    Rook: 'rook',
    Knight: 'knight',
    Bishop: 'bishop',
    Queen: 'queen',
    King: 'king'
}

# Load images for chess pieces (e.g., 'assets/white_pawn.png')
def load_piece_images():
    pieces = {}
    for color in ['white', 'black']:
        for piece in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
            path = f'assets/{color}_{piece}.png'
            image = pygame.image.load(path)
            resized_image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            pieces[f"{color}_{piece}"] = resized_image
    return pieces

# Draw the chessboard
def draw_board(win):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw the pieces on the board
def draw_pieces(win, board, pieces):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.board[row][col]
            if isinstance(piece, Piece):  # Ensure it's an instance of Piece
                piece_type = PIECE_TYPE_MAP.get(type(piece))
                if piece_type:
                    piece_key = f"{piece.color}_{piece_type}"
                    piece_image = pieces.get(piece_key)
                    if piece_image:
                        piece_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                        win.blit(piece_image, piece_rect.topleft)

# Highlight valid moves with different colors for regular and capture moves
def highlight_moves(win, moves, board, selected_piece, king_position, turn):
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)  # Allow transparency
    attacking_piece = None

    if king_position:
        # Find the attacking piece (that is checking the king)
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color != turn:  # Opponent's pieces
                    if (king_position[0], king_position[1]) in piece.valid_moves((row, col), board):
                        attacking_piece = piece
                        break

    # If the king is in check, highlight only valid blocking/capture moves
    if attacking_piece:
        can_block_or_capture = False
        for move in moves:
            row, col = move
            target_piece = board.board[row][col]
            
            # If this move can block or capture the attacking piece, highlight it
            if target_piece is None or target_piece.color != selected_piece.color:
                # Implement logic to check if a piece can block the attack or capture the attacking piece
                if is_blocking_move(move, attacking_piece, king_position, board) or \
                   is_capturing_move(move, attacking_piece, board):
                    can_block_or_capture = True
                    highlight_surface.fill(HIGHLIGHT_COLOR)  # Green for block or capture
                    win.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                else:
                    continue
        if not can_block_or_capture:
            return  # If no valid block/capture moves, return without highlighting
    else:
        # Otherwise, highlight all valid moves normally
        for move in moves:
            row, col = move
            target_piece = board.board[row][col]
            
            # If target square contains a piece and it's an opponent's piece, it's a capture
            if target_piece is not None and target_piece.color != selected_piece.color:
                highlight_surface.fill(CAPTURE_COLOR)  # Red for capture
            elif target_piece is None:
                highlight_surface.fill(HIGHLIGHT_COLOR)  # Green for regular moves
            else:
                continue

            win.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def is_blocking_move(move, attacking_piece, king_position, board):
    """Check if the move can block the check on the king"""
    # Get the direction of the attacking piece's movement (relative to the king)
    attacking_row, attacking_col = king_position
    block_row, block_col = move  # The square that may block the attack

    # Direction vectors for horizontal, vertical, and diagonal directions
    direction_vectors = {
        'vertical': [(1, 0), (-1, 0)],
        'horizontal': [(0, 1), (0, -1)],
        'diagonal': [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    }

    # Depending on the type of attacking piece (e.g., rook, bishop, queen), we need to check
    # if the move is between the attacker and the king.

    if isinstance(attacking_piece, (Rook, Queen)):  # Horizontal or vertical attack
        if attacking_row == block_row:  # Same row
            if min(attacking_col, block_col) < block_col < max(attacking_col, block_col):
                # Check if there is any piece between the attacker and the king in this row
                for col in range(min(attacking_col, block_col) + 1, max(attacking_col, block_col)):
                    if board.board[block_row][col] is not None:
                        return False  # There is a piece in the way, cannot block
                return True  # No pieces in the way, valid block move
        elif attacking_col == block_col:  # Same column
            if min(attacking_row, block_row) < block_row < max(attacking_row, block_row):
                # Check if there is any piece between the attacker and the king in this column
                for row in range(min(attacking_row, block_row) + 1, max(attacking_row, block_row)):
                    if board.board[row][block_col] is not None:
                        return False  # There is a piece in the way, cannot block
                return True  # No pieces in the way, valid block move

    elif isinstance(attacking_piece, (Bishop, Queen)):  # Diagonal attack
        if abs(attacking_row - block_row) == abs(attacking_col - block_col):
            row_step = 1 if block_row > attacking_row else -1
            col_step = 1 if block_col > attacking_col else -1
            # Check if there is any piece between the attacker and the king along the diagonal
            curr_row, curr_col = attacking_row + row_step, attacking_col + col_step
            while (curr_row, curr_col) != (block_row, block_col):
                if board.board[curr_row][curr_col] is not None:
                    return False  # There is a piece in the way, cannot block
                curr_row += row_step
                curr_col += col_step
            return True  # No pieces in the way, valid block move
    return False  # If none of the conditions match, it's not a valid block


def is_capturing_move(move, attacking_piece, board):
    """Check if the move can capture the attacking piece"""
    row, col = move
    target_piece = board.board[row][col]
    if target_piece and target_piece == attacking_piece:
        return True
    return False

# Reset the board to the initial setup
def reset_board(board):
    # Reinitialize the board from scratch by clearing it first
    board.board = [[None for _ in range(8)] for _ in range(8)]  # Clear the board
    board.setup()  # Reapply the initial setup
    return None, None, 'white'

# Check if the game is over (e.g., checkmate or stalemate)
def is_game_over(board):
    # Implement game over logic here
    return False

def find_king(board, color):
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if isinstance(piece, King) and piece.color == color:
                return row, col
    return None  # King not found (should never happen if the board is set up correctly)


# Main game loop
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    pieces = load_piece_images()

    # Initialize chess board
    board = Board()
    board.setup()

    selected_piece = None
    selected_pos = None
    turn = 'white'

    # Create an instance of Rules to check for check
    rules = Rules()
    checkmate=False
    font = pygame.font.SysFont(None, 75)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                if selected_piece:
                    # Check if the move is valid and king is not in check after move
                    valid_moves = selected_piece.valid_moves(selected_pos, board)
                    if (row, col) in valid_moves:
                        # Apply the move
                        board.board[selected_pos[0]][selected_pos[1]] = None
                        board.board[row][col] = selected_piece
                        
                        # Check if the move results in the king being in check
                        king_pos = find_king(board, selected_piece.color)
                        if king_pos:
                            if rules.is_check(board,king_pos,selected_piece.color):
                                # Undo the move if king is in check
                                board.board[row][col] = None
                                board.board[selected_pos[0]][selected_pos[1]] = selected_piece
                                print("Move would result in check! Try again.")
                            else:
                                # Switch turns
                                turn = 'black' if turn == 'white' else 'white'
                        
                            selected_piece = None
                            selected_pos = None  # Reset selected piece and position after a move
                    else:
                        selected_piece = None
                        selected_pos = None  # Reset if the move is not valid, deselect the piece
                else:
                    piece = board.board[row][col]
                    if piece and piece.color == turn:
                        selected_piece = piece
                        selected_pos = (row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press 'R' to reset the game
                    selected_piece, selected_pos, turn = reset_board(board)
                    checkmate = False
                elif event.key == pygame.K_z:  # Press 'Z' to display checkmate
                    checkmate = True
                    

        draw_board(win)
        if selected_piece:
            valid_moves = selected_piece.valid_moves(selected_pos, board)
            highlight_moves(win, valid_moves, board, selected_piece, find_king(board, selected_piece.color), turn)
        draw_pieces(win, board, pieces)

        if checkmate:
            checkmate_text = font.render("Checkmate!", True, (255, 0, 0))  # Red color
            win.blit(checkmate_text, (WIDTH // 2 - checkmate_text.get_width() // 2, HEIGHT // 2 - checkmate_text.get_height() // 2))

        if is_game_over(board):
            print("Game Over")
            running = False
        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
