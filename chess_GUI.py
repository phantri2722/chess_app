import pygame
import chess
import chess.svg

SQUARE_SIZE = 60
BOARD_SIZE = SQUARE_SIZE * 8

WHITE = (238, 238, 210)
BLACK = (118, 150, 86)

piece_images = {}
pieces = ['p', 'r', 'n', 'b', 'q', 'k', 'P', 'R', 'N', 'B', 'Q', 'K']

# Load hình ảnh quân cờ
piece_images = {
    "p": pygame.image.load("pieces/bP.png"),
    "r": pygame.image.load("pieces/bR.png"),
    "n": pygame.image.load("pieces/bN.png"),
    "b": pygame.image.load("pieces/bB.png"),
    "q": pygame.image.load("pieces/bQ.png"),
    "k": pygame.image.load("pieces/bK.png"),
    "P": pygame.image.load("pieces/wP.png"),
    "R": pygame.image.load("pieces/wR.png"),
    "N": pygame.image.load("pieces/wN.png"),
    "B": pygame.image.load("pieces/wB.png"),
    "Q": pygame.image.load("pieces/wQ.png"),
    "K": pygame.image.load("pieces/wK.png"),
}

for piece in pieces:
    piece_images[piece] = pygame.transform.scale(piece_images[piece], (SQUARE_SIZE, SQUARE_SIZE))

pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))

board = chess.Board()

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)  # Chuyển tọa độ hàng cột thành chỉ mục bàn cờ
            piece = board.piece_at(square)  # Lấy quân cờ tại ô đó
            
            if piece:  # Nếu có quân cờ
                screen.blit(piece_images[piece.symbol()], (col * SQUARE_SIZE, row * SQUARE_SIZE))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    draw_pieces()
    pygame.display.flip()

pygame.quit()
