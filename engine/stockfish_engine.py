# engine/stockfish_engine.py
import chess
import chess.engine
import os

class StockfishAI:
    def __init__(self, path="D:/chess_app/engine/stockfish-windows-x86-64-avx2.exe", time_limit=1.0):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy engine tại {path}")
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.time_limit = time_limit

    def get_best_move(self, board: chess.Board):
        result = self.engine.play(board, chess.engine.Limit(time=self.time_limit))
        return result.move

    def quit(self):
        self.engine.quit()
