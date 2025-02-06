import pygame
from chess.board import Board
from chess.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King

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
def highlight_moves(win, moves, board, selected_piece):
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)  # Allow transparency
    for move in moves:
        row, col = move
        target_piece = board.board[row][col]
        
        # If target square contains a piece and it's an opponent's piece, it's a capture
        if target_piece is not None and target_piece.color != selected_piece.color:
            highlight_surface.fill(CAPTURE_COLOR)  # Red for capture
        elif target_piece is None:
            highlight_surface.fill(HIGHLIGHT_COLOR)  # Green for regular moves
        else:
            # If target square contains the same color piece, no need to highlight
            continue
        
        win.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                if selected_piece:
                    valid_moves = selected_piece.valid_moves(selected_pos, board)
                    if (row, col) in valid_moves:
                        board.board[selected_pos[0]][selected_pos[1]] = None
                        board.board[row][col] = selected_piece
                        turn = 'black' if turn == 'white' else 'white'
                    selected_piece = None
                    selected_pos = None
                else:
                    piece = board.board[row][col]
                    if piece and piece.color == turn:
                        selected_piece = piece
                        selected_pos = (row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press 'R' to reset the game
                    selected_piece, selected_pos, turn = reset_board(board)

        draw_board(win)
        if selected_piece:
            valid_moves = selected_piece.valid_moves(selected_pos , board)
            highlight_moves(win, valid_moves, board, selected_piece)
        draw_pieces(win, board, pieces)
        if is_game_over(board):
            print("Game Over")
            running = False
        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
