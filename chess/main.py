# Xử lý giao diện và tương tác của người dùng trong trò chơi

import sys
import pygame as p
from bases import GameState, Move
from bot_v2 import findRandomMoves, findBestMove
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

# Green color
LIGHT_SQUARE_COLOR = (237, 238, 209)
DARK_SQUARE_COLOR = (119, 153, 82)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)


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
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color(MOVE_HIGHLIGHT_COLOR))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
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
    padding = 10  
    lineSpacing = 5  
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]

        textObject = font.render(text, True, p.Color('black'))

        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)

        textY += textObject.get_height() + lineSpacing

 
# Hiển thị khi kết thúc trò chơi
def drawEndGameText(screen, text):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    textObject = font.render(text, True, p.Color('black'))

    text_width = textObject.get_width()
    text_height = textObject.get_height()

    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_width/2, BOARD_HEIGHT/2 - text_height/2)

    screen.blit(textObject, textLocation)

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
        # Lượt đi của người chơi
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or (
            not gs.whiteToMove and playerBlackHuman)
        
        # Xử lý sự kiện
        for e in p.event.get():
            # Sự kiện thoát game
            if e.type == p.QUIT:
                running = False
            # Sự kiện click chuột
            elif e.type == p.MOUSEBUTTONDOWN:
                # Khi game chưa kết thúc
                if not gameOver:  
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    # Khi người chơi click chuột vào cùng 1 ô vuông 2 lần hoặc click chuột vào ô vuông ngoài bàn cờ
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()  
                        playerClicks = []  
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    # Khi người chơi click chuột lần thứ 2 (đích)
                    if len(playerClicks) == 2 and humanTurn:
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            # Nước đi hợp lệ
                            if move == validMoves[i]:
                                # Khi quân cờ đã được chọn và người chơi click chuột vào ô vuông có quân cờ khác --> ăn quân
                                if gs.board[validMoves[i].endRow][validMoves[i].endCol] != '--':
                                    pieceCaptured = True
                                gs.makeMove(validMoves[i])
                                # Khi nước đi là phong cấp tốt
                                if (move.isPawnPromotion):
                                    promotion_choice = pawnPromotionPopup(
                                        screen, gs)
                                    gs.board[move.endRow][move.endCol] = move.pieceMoved[0] + \
                                        promotion_choice
                                    promote_sound.play()
                                    pieceCaptured = False

                                # Hiệu ứng âm thanh cho nước đi
                                if (pieceCaptured or move.isEnpassantMove):
                                    capture_sound.play()
                                elif not move.isPawnPromotion:
                                    move_sound.play()

                                # Đưa các giá trị về mặc định
                                pieceCaptured = False
                                moveMade = True
                                squareSelected = ()
                                playerClicks = []
                        # Nếu nước đi chưa được thực hiện
                        if not moveMade:
                            playerClicks = [squareSelected]

            # Sự kiện bàn phím
            elif e.type == p.KEYDOWN:
                # Bấm phím Z --> hoàn tác nước đi
                if e.key == p.K_z:  
                    gs.undoMove()
                    # Khi hoàn tác nước đi thì ta phải cập nhật lại danh sách các nước đi hợp lệ
                    moveMade = True
                    gameOver = False
                    # Nếu đang lượt đi của AI --> dừng lại
                    if AIThinking:
                        moveFinderProcess.terminate()  
                        AIThinking = False
                    moveUndone = True
                # Bấm phím R --> khởi động lại bàn cờ
                if e.key == p.K_r:  
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    # Néu đang lượt đi của AI --> dừng lại
                    if AIThinking:
                        moveFinderProcess.terminate()  
                        AIThinking = False
                    moveUndone = True

        # Nếu không phải lượt của người chơi và không có nước đi nào được thực hiện
        if not gameOver and not humanTurn and not moveUndone:
            # Nếu AI đang suy nghĩ --> gọi hàm tìm nước đi tốt nhất và bắt đầu quy trình tìm kiếm nước đi của AI
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  
                moveFinderProcess = Process(target=findBestMove, args=(
                    gs, validMoves, returnQueue))  
                moveFinderProcess.start()
            # Nếu quy trình tìm kiếm nước đi của AI đã hoàn thành
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                # Nếu không tìm thấy nước đi nào tốt --> tìm nước đi ngẫu nhiên
                if AIMove is None:
                    AIMove = findRandomMoves(validMoves)
                # Nếu đích đến nước đi của AI chứa quân cờ của đối phương --> ăn quân
                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True
                
                # Thực hiện nước đi của AI
                gs.makeMove(AIMove)

                # Nếu nước đi của AI là phong cấp tốt
                if AIMove.isPawnPromotion:
                    promotion_choice = pawnPromotionPopup(screen, gs)
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + \
                        promotion_choice
                    promote_sound.play()
                    pieceCaptured = False

                # Hiệu ứng âm thanh cho nước đi
                if (pieceCaptured or AIMove.isEnpassantMove):
                    capture_sound.play()
                elif not AIMove.isPawnPromotion:
                    move_sound.play()

                # Đưa các giá trị về mặc định
                pieceCaptured = False
                AIThinking = False
                moveMade = True
                squareSelected = ()
                playerClicks = []

        # Nếu nước đi đã được thực hiện
        if moveMade:
            # Trong cờ vua, ván đấu sẽ hoà nếu cùng một vị trí trên bàn cờ được lặp lại 3 lần (không nhất thiết phải liên tiếp nhau) --> kiểm tra mỗi 4 nước đi
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
            
            # Tạo lại danh sách các nước đi hợp lệ khi nước đi đã được thực hiện
            validMoves = gs.getValidMoves()
            moveMade = False
            moveUndone = False

        # Vẽ trạng thái trò chơi
        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        # Hoà
        if COUNT_DRAW == 1:
            gameOver = True
            text = 'Draw due to repetition'
            drawEndGameText(screen, text)
        # Hết nước đi
        if gs.stalemate:
            gameOver = True
            text = 'Stalemate'
            drawEndGameText(screen, text)
        # Chiếu hết
        elif gs.checkmate:
            gameOver = True
            text = 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


# Chạy chương trình
if __name__ == "__main__":
    main()
