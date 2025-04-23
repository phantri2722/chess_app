# Xử lý giao diện và tương tác của người dùng trong trò chơi

import sys
import pygame as p
from bases import GameState, Move
from bot import findRandomMoves, findBestMove
from multiprocessing import Process, Queue

# Hiệu ứng âm thanh
p.mixer.init()
move_sound = p.mixer.Sound("sounds/move-sound.mp3")
capture_sound = p.mixer.Sound("sounds/capture.mp3")
promote_sound = p.mixer.Sound("sounds/promote.mp3")

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

SET_WHITE_AS_BOT = False
SET_BLACK_AS_BOT = False

# Define colors

# 1 Green

LIGHT_SQUARE_COLOR = (237, 238, 209)
DARK_SQUARE_COLOR = (119, 153, 82)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)

# 2 Brown

'''
LIGHT_SQUARE_COLOR = (240, 217, 181)
DARK_SQUARE_COLOR = (181, 136, 99)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)
'''

# 3 Gray

'''
LIGHT_SQUARE_COLOR = (220,220,220)
DARK_SQUARE_COLOR = (170,170,170)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (164,184,196)
'''

# Tải ảnh quân cờ
def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK',
              'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        image_path = "images/" + piece + ".png"
        original_image = p.image.load(image_path)
        IMAGES[piece] = p.transform.smoothscale(
            original_image, (SQ_SIZE, SQ_SIZE))

# Xử lý phong cấp tốt
def pawnPromotionPopup(screen, gs):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    text = font.render("Choose promotion:", True, p.Color("black"))

    # Tạo các nút cho các quân cờ
    button_width, button_height = 100, 100
    buttons = [
        p.Rect(100, 200, button_width, button_height),
        p.Rect(200, 200, button_width, button_height),
        p.Rect(300, 200, button_width, button_height),
        p.Rect(400, 200, button_width, button_height)
    ]

    if gs.whiteToMove:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images/bQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images/bR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images/bB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images/bN.png"), (100, 100))
        ]
    else:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images/wQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images/wR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images/wB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images/wN.png"), (100, 100))
        ]

    # Vòng lặp chính hiển thị popup
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = e.pos
                for i, button in enumerate(buttons):
                    if button.collidepoint(mouse_pos):
                        if i == 0:
                            return "Q"  # Return the index of the selected piece
                        elif i == 1:
                            return "R"
                        elif i == 2:
                            return "B"
                        else:
                            return "N"

        # Hiển thị popup
        screen.fill(p.Color(LIGHT_SQUARE_COLOR))
        screen.blit(text, (110, 150))
        for i, button in enumerate(buttons):
            p.draw.rect(screen, p.Color("white"), button)
            screen.blit(button_images[i], button.topleft)

        p.display.flip()

# Vẽ trạng thái trò chơi
def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont):
    drawSquare(screen)  # draw square on board
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)

# Vẽ bàn cờ với các ô vuông sáng và tối
def drawSquare(screen):
    global colors
    colors = [p.Color(LIGHT_SQUARE_COLOR), p.Color(DARK_SQUARE_COLOR)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Đánh dấu ô vuông được chọn và các ô vuông có thể di chuyển
def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():  
        row, col = squareSelected
        
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected piece square
            # Surface in pygame used to add images or transperency feature
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            # set_alpha --> transperancy value (0 transparent)
            s.set_alpha(100)
            s.fill(p.Color(MOVE_HIGHLIGHT_COLOR))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            # highlighting valid square
            s.fill(p.Color(POSSIBLE_MOVE_COLOR))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

# Vẽ các quân cờ trên bàn cờ
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Hiển thị lịch sử các nước đi
def drawMoveLog(screen, gs, font):
    # rectangle
    moveLogRect = p.Rect(
        BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color(LIGHT_SQUARE_COLOR), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = " " + str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 10  # Increase padding for better readability
    lineSpacing = 5  # Increase line spacing for better separation
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]

        textObject = font.render(text, True, p.Color('black'))

        # Adjust text location based on padding and line spacing
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)

        # Update Y coordinate for the next line with increased line spacing
        textY += textObject.get_height() + lineSpacing

 
# Hiển thị khi kết thúc trò chơi
def drawEndGameText(screen, text):
    # create font object with type and size of font you want
    font = p.font.SysFont("Times New Roman", 30, False, False)
    # use the above font and render text (0 ? antialias)
    textObject = font.render(text, True, p.Color('black'))

    # Get the width and height of the textObject
    text_width = textObject.get_width()
    text_height = textObject.get_height()

    # Calculate the position to center the text on the screen
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_width/2, BOARD_HEIGHT/2 - text_height/2)

    # Blit the textObject onto the screen at the calculated position
    screen.blit(textObject, textLocation)

    # Create a second rendering of the text with a slight offset for a shadow effect
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(1, 1))


def main():
    # Khởi tạo game
    p.init()
    screen = p.display.set_mode(
        (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color(LIGHT_SQUARE_COLOR))
    moveLogFont = p.font.SysFont("Times New Roman", 12, False, False)

    # Tạo một đối tượng GameState để theo dõi trạng thái của trò chơi
    gs = GameState()
    if (gs.playerWantsToPlayAsBlack):
        gs.board = gs.board1

    validMoves = gs.getValidMoves()
    moveMade = False  # Nếu người chơi đã thực hiện một nước đi thì chúng ta cần tạo ra một danh sách các nước đi hợp lệ mới
    loadImages()
    running = True
    squareSelected = ()  # Đánh dấu lần cuối click chuột
    playerClicks = []
    gameOver = False  
    playerWhiteHuman = not SET_WHITE_AS_BOT
    playerBlackHuman = not SET_BLACK_AS_BOT
    AIThinking = False  
    moveFinderProcess = None 
    moveUndone = False
    pieceCaptured = False
    positionHistory = "" 
    previousPos = ""
    countMovesForDraw = 0 
    COUNT_DRAW = 0
    while running:
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or (
            not gs.whiteToMove and playerBlackHuman)
        
        # Xử lý sự kiện
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Xử lý click chuột
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:  
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    # if user clicked on same square twice or user click outside board
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        squareSelected = (row, col)
                        # append player both clicks (place and destination)
                        playerClicks.append(squareSelected)
                    # after second click (at destination)
                    if len(playerClicks) == 2 and humanTurn:
                        # user generated a move
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            # check if the move is in the validMoves
                            if move == validMoves[i]:
                                # Check if a piece is captured at the destination square
                                # print(gs.board[validMoves[i].endRow][validMoves[i].endCol])
                                if gs.board[validMoves[i].endRow][validMoves[i].endCol] != '--':
                                    pieceCaptured = True
                                gs.makeMove(validMoves[i])
                                if (move.isPawnPromotion):
                                    # Show pawn promotion popup and get the selected piece
                                    promotion_choice = pawnPromotionPopup(
                                        screen, gs)
                                    # Set the promoted piece on the board
                                    gs.board[move.endRow][move.endCol] = move.pieceMoved[0] + \
                                        promotion_choice
                                    promote_sound.play()
                                    pieceCaptured = False
                                # add sound for human move
                                if (pieceCaptured or move.isEnpassantMove):
                                    # Play capture sound
                                    capture_sound.play()
                                    # print("capture sound")
                                elif not move.isPawnPromotion:
                                    # Play move sound
                                    move_sound.play()
                                    # print("move sound")
                                pieceCaptured = False
                                moveMade = True
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]

            # Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    # when user undo move valid move change, here we could use [ validMoves = gs.getValidMoves() ] which would update the current validMoves after undo
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()  # terminate the ai thinking if we undo
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # reset board when 'r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()  # terminate the ai thinking if we undo
                        AIThinking = False
                    moveUndone = True

        # AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # keep track of data, to pass data between threads
                moveFinderProcess = Process(target=findBestMove, args=(
                    gs, validMoves, returnQueue))  # when processing start we call these process
                # call findBestMove(gs, validMoves, returnQueue) #rest of the code could still work even if the ai is thinking
                moveFinderProcess.start()
                # AIMove = findBestMove(gs, validMoves)
                # gs.makeMove(AIMove)
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()  # return from returnQueue
                if AIMove is None:
                    AIMove = findRandomMoves(validMoves)

                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True

                gs.makeMove(AIMove)

                if AIMove.isPawnPromotion:
                    # Show pawn promotion popup and get the selected piece
                    promotion_choice = pawnPromotionPopup(screen, gs)
                    # Set the promoted piece on the board
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + \
                        promotion_choice
                    promote_sound.play()
                    pieceCaptured = False

                # add sound for human move
                if (pieceCaptured or AIMove.isEnpassantMove):
                    # Play capture sound
                    capture_sound.play()
                    # print("capture sound")
                elif not AIMove.isPawnPromotion:
                    # Play move sound
                    move_sound.play()
                    # print("move sound")
                pieceCaptured = False
                AIThinking = False
                moveMade = True
                animate = True
                squareSelected = ()
                playerClicks = []

        if moveMade:
            if countMovesForDraw == 0 or countMovesForDraw == 1 or countMovesForDraw == 2 or countMovesForDraw == 3:
                countMovesForDraw += 1
            if countMovesForDraw == 4:
                positionHistory += gs.getBoardString()
                if previousPos == positionHistory:
                    COUNT_DRAW += 1
                    positionHistory = ""
                    countMovesForDraw = 0
                else:
                    previousPos = positionHistory
                    positionHistory = ""
                    countMovesForDraw = 0
                    COUNT_DRAW = 0
            
            # genetare new set of valid move if valid move is made
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        if COUNT_DRAW == 1:
            gameOver = True
            text = 'Draw due to repetition'
            drawEndGameText(screen, text)
        if gs.stalemate:
            gameOver = True
            text = 'Stalemate'
            drawEndGameText(screen, text)
        elif gs.checkmate:
            gameOver = True
            text = 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()





# if we import main then main function wont run it will run only while running this file
if __name__ == "__main__":
    main()
