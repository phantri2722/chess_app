# training_ai.py
import importlib
import json
from datetime import datetime
from bases import GameState, Move
from multiprocessing import Queue

# Load bot module by name
def load_bot(module_name):
    return importlib.import_module(module_name)

# Chạy 1 ván đấu giữa hai bot

def play_match(bot1, bot2, bot1_plays_white=True):
    gs = GameState()
    white_bot = bot1 if bot1_plays_white else bot2
    black_bot = bot2 if bot1_plays_white else bot1

    move_limit = 200
    for _ in range(move_limit):
        if gs.checkmate or gs.stalemate:
            break

        current_bot = white_bot if gs.whiteToMove else black_bot

        # Đặt hướng đúng cho AI chuẩn bị đánh
        gs.playerWantsToPlayAsBlack = (current_bot == black_bot)

        valid_moves = gs.getValidMoves()
        if len(valid_moves) == 0:
            break

        q = Queue()
        current_bot.findBestMove(gs, valid_moves, q)
        move = q.get()

        if move is None:
            break
        gs.makeMove(move)

    if gs.checkmate:
        return 1 if not gs.whiteToMove else -1
    return 0  # draw or stalemate



# Chạy nhiều ván giữa 2 bot

def evaluate_bots(bot1_name, bot2_name, num_games=20):
    bot1 = load_bot(bot1_name)
    bot2 = load_bot(bot2_name)

    results = {"bot1_win": 0, "bot2_win": 0, "draw": 0}

    for i in range(num_games):
        bot1_first = i % 2 == 0
        result = play_match(bot1, bot2, bot1_plays_white=bot1_first)
        if result == 1:
            results["bot1_win"] += 1
        elif result == -1:
            results["bot2_win"] += 1
        else:
            results["draw"] += 1

    log_result(bot1_name, bot2_name, results)
    return results


# Ghi log vào file

def log_result(bot1, bot2, result, file="training_log.json"):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "bot1": bot1,
        "bot2": bot2,
        "results": result
    }
    with open(file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print("Log written:", entry)


if __name__ == "__main__":
    summary = evaluate_bots("bot_v2", "bot_v3", num_games=20  )
    print("Match Result Summary:", summary)