import chess
import chess.engine
from bot_v2 import findBestMove
from bases import GameState, Move
from multiprocessing import Queue
import time
import json
import os

STOCKFISH_PATH = "path/to/stockfish.exe"  # <<< đường dẫn đến stockfish.exe của bạn

def botMove(gs):
    validMoves = gs.getValidMoves()
    returnQueue = Queue()
    findBestMove(gs, validMoves, returnQueue)
    return returnQueue.get()

def stockfishMove(board, engine):
    result = engine.play(board, chess.engine.Limit(time=1))  # cho stockfish 1 giây mỗi nước đi
    return result.move

def convertMove(moveUCI, gs):
    # Chuyển nước dạng UCI từ stockfish thành nước Move của GameState của bạn
    startCol = ord(moveUCI.uci()[0]) - ord('a')
    startRow = 8 - int(moveUCI.uci()[1])
    endCol = ord(moveUCI.uci()[2]) - ord('a')
    endRow = 8 - int(moveUCI.uci()[3])
    return Move((startRow, startCol), (endRow, endCol), gs.board)

def playGame(bot_white=True, stockfish_level=1):
    gs = GameState()
    board = chess.Board()

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    engine.configure({"Skill Level": stockfish_level})  # chỉnh mức skill 0-20

    result = None

    while not gs.checkmate and not gs.stalemate:
        if (gs.whiteToMove and bot_white) or (not gs.whiteToMove and not bot_white):
            move = botMove(gs)
            gs.makeMove(move)
            board.push_uci(move.getChessNotationForEngine())  # cần hàm getChessNotationForEngine() trong Move
        else:
            move = stockfishMove(board, engine)
            gs.makeMove(convertMove(move, gs))
            board.push(move)

    if gs.checkmate:
        if gs.whiteToMove:
            result = "Stockfish wins"
        else:
            result = "Bot wins"
    else:
        result = "Draw"

    engine.quit()
    return result

if __name__ == "__main__":
    num_games = 20
    bot_white = True  # Cho bot cầm trắng trước

    results = {"Bot wins": 0, "Stockfish wins": 0, "Draw": 0}

    for i in range(num_games):
        print(f"Game {i+1} starting...")
        result = playGame(bot_white, stockfish_level=1)  # Skill level thấp
        results[result] += 1
        bot_white = not bot_white  # Đổi bên mỗi trận

    print("=== Final results ===")
    print(results)
