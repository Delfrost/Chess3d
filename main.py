import pygame
from chess.board import Board
from chess.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from chess.rules import Rules  

pygame.init()

WIDTH, HEIGHT = 800, 800  
ROWS, COLS = 8, 8         
SQUARE_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (50, 205, 50, 128) 
CAPTURE_COLOR = (255, 0, 0, 128)      

PIECE_TYPE_MAP = {
    Pawn: 'pawn',
    Rook: 'rook',
    Knight: 'knight',
    Bishop: 'bishop',
    Queen: 'queen',
    King: 'king'
}

def load_piece_images():
    pieces = {}
    for color in ['white', 'black']:
        for piece in ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']:
            path = f'assets/{color}_{piece}.png'
            image = pygame.image.load(path)
            resized_image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            pieces[f"{color}_{piece}"] = resized_image
    return pieces

def draw_board(win):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(win, board, pieces):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.board[row][col]
            if isinstance(piece, Piece):  
                piece_type = PIECE_TYPE_MAP.get(type(piece))
                if piece_type:
                    piece_key = f"{piece.color}_{piece_type}"
                    piece_image = pieces.get(piece_key)
                    if piece_image:
                        piece_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                        win.blit(piece_image, piece_rect.topleft)

def highlight_moves(win, moves, board, selected_piece, king_position, turn):
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)  
    attacking_piece = None

    if king_position:
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color != turn:  
                    if (king_position[0], king_position[1]) in piece.valid_moves((row, col), board):
                        attacking_piece = piece
                        break

    if attacking_piece:
        can_block_or_capture = False
        for move in moves:
            row, col = move
            target_piece = board.board[row][col]
            if target_piece is None or target_piece.color != selected_piece.color:
                if is_blocking_move(move, attacking_piece, king_position, board) or \
                   is_capturing_move(move, attacking_piece, board):
                    can_block_or_capture = True
                    highlight_surface.fill(HIGHLIGHT_COLOR)  
                    win.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                else:
                    continue
        if not can_block_or_capture:
            return  
    else:
        for move in moves:
            row, col = move
            target_piece = board.board[row][col]
            if target_piece is not None and target_piece.color != selected_piece.color:
                highlight_surface.fill(CAPTURE_COLOR)  
            elif target_piece is None:
                highlight_surface.fill(HIGHLIGHT_COLOR)  
            else:
                continue
            win.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def is_blocking_move(move, attacking_piece, king_position, board):
    attacking_row, attacking_col = king_position
    block_row, block_col = move  

    direction_vectors = {
        'vertical': [(1, 0), (-1, 0)],
        'horizontal': [(0, 1), (0, -1)],
        'diagonal': [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    }

    if isinstance(attacking_piece, (Rook, Queen)):  
        if attacking_row == block_row:  
            if min(attacking_col, block_col) < block_col < max(attacking_col, block_col):
                for col in range(min(attacking_col, block_col) + 1, max(attacking_col, block_col)):
                    if board.board[block_row][col] is not None:
                        return False  
                return True  
        elif attacking_col == block_col:
            if min(attacking_row, block_row) < block_row < max(attacking_row, block_row):
                for row in range(min(attacking_row, block_row) + 1, max(attacking_row, block_row)):
                    if board.board[row][block_col] is not None:
                        return False  
                return True  

    elif isinstance(attacking_piece, (Bishop, Queen)):
        if abs(attacking_row - block_row) == abs(attacking_col - block_col):
            row_step = 1 if block_row > attacking_row else -1
            col_step = 1 if block_col > attacking_col else -1
            curr_row, curr_col = attacking_row + row_step, attacking_col + col_step
            while (curr_row, curr_col) != (block_row, block_col):
                if board.board[curr_row][curr_col] is not None:
                    return False  
                curr_row += row_step
                curr_col += col_step
            return True  
    return False  

def is_capturing_move(move, attacking_piece, board):
    row, col = move
    target_piece = board.board[row][col]
    if target_piece and target_piece == attacking_piece:
        return True
    return False

def reset_board(board):
    board.board = [[None for _ in range(8)] for _ in range(8)]  
    board.setup()  
    return None, None, 'white'

def is_game_over(board):
    return False

def find_king(board, color):
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if isinstance(piece, King) and piece.color == color:
                return row, col
    return None  

def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    pieces = load_piece_images()

    board = Board()
    board.setup()

    selected_piece = None
    selected_pos = None
    turn = 'white'

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
                    valid_moves = selected_piece.valid_moves(selected_pos, board)
                    if (row, col) in valid_moves:
                        board.board[selected_pos[0]][selected_pos[1]] = None
                        board.board[row][col] = selected_piece
                        king_pos = find_king(board, selected_piece.color)
                        if king_pos:
                            if rules.is_check(board,king_pos,selected_piece.color):
                                board.board[row][col] = None
                                board.board[selected_pos[0]][selected_pos[1]] = selected_piece
                                print("Move would result in check! Try again.")
                            else:
                                turn = 'black' if turn == 'white' else 'white'
                        selected_piece = None
                        selected_pos = None  
                    else:
                        selected_piece = None
                        selected_pos = None  
                else:
                    piece = board.board[row][col]
                    if piece and piece.color == turn:
                        selected_piece = piece
                        selected_pos = (row, col)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    selected_piece, selected_pos, turn = reset_board(board)
                    checkmate = False
                elif event.key == pygame.K_z:
                    checkmate = True

        draw_board(win)
        if selected_piece:
            valid_moves = selected_piece.valid_moves(selected_pos, board)
            highlight_moves(win, valid_moves, board, selected_piece, find_king(board, selected_piece.color), turn)
        draw_pieces(win, board, pieces)

        if checkmate:
            checkmate_text = font.render("Checkmate!", True, (255, 0, 0))  
            win.blit(checkmate_text, (WIDTH // 2 - checkmate_text.get_width() // 2, HEIGHT // 2 - checkmate_text.get_height() // 2))

        if is_game_over(board):
            print("Game Over")
            running = False
        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
