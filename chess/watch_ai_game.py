# watch_ai_game.py
import pygame as p
from multiprocessing import Queue
from bases import GameState, Move
from bot_v1 import findBestMove

WIDTH, HEIGHT = 512, 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
FPS = 10
IMAGES = {}


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK',
              'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


def watch_ai_vs_ai(bot1, bot2, delay=0.5):
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    loadImages()

    gs = GameState()
    gs.playerWantsToPlayAsBlack = False

    bots = [bot1, bot2]
    running = True
    move_count = 0

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        drawGameState(screen, gs)
        p.display.flip()

        if gs.checkmate:
            print("Checkmate.", "Black wins." if gs.whiteToMove else "White wins.")
            running = False
        elif gs.stalemate:
            print("Stalemate.")
            running = False
        else:
            q = Queue()
            bot = bots[move_count % 2]
            validMoves = gs.getValidMoves()
            bot.findBestMove(gs, validMoves, q)
            move = q.get()
            if move is None:
                print("Bot returned no move.")
                running = False
            else:
                gs.makeMove(move)
                move_count += 1
                p.time.wait(int(delay * 1000))

        clock.tick(FPS)

    p.quit()


if __name__ == "__main__":
    import bot_v1 as bot1
    import bot_v2 as bot2
    watch_ai_vs_ai(bot1, bot2, delay=0.7)