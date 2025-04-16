import chess
import chess.engine

# Đường dẫn tới file stockfish.exe (cập nhật đúng đường dẫn của bạn)
STOCKFISH_PATH = "D:\stockfish\stockfish-windows-x86-64-avx2.exe"  

# Khởi tạo bàn cờ
board = chess.Board()

# Kết nối engine
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

print("Bắt đầu chơi cờ! Bạn là Trắng (đi trước). Nhập nước theo chuẩn UCI (vd: e2e4)")
print(board)

# Bắt đầu vòng lặp
while not board.is_game_over():
    # --- Người chơi ---
    while True:
        user_move = input("Bạn đi: ")
        try:
            move = chess.Move.from_uci(user_move)
            if move in board.legal_moves:
                board.push(move)
                break
            else:
                print("Nước đi không hợp lệ, thử lại!")
        except:
            print("Sai cú pháp, thử lại (vd: e2e4)")

    print("Sau khi bạn đi:")
    print(board)

    if board.is_game_over():
        break

    # --- AI chơi ---
    print("AI đang suy nghĩ...")
    result = engine.play(board, chess.engine.Limit(time=2.0))  # max 2s
    board.push(result.move)
    print(f"AI đi: {result.move}")
    print(board)

# --- Kết thúc ---
print("Trận đấu kết thúc!")
print("Kết quả:", board.result())

engine.quit()
