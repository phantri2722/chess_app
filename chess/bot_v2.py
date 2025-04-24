# bot_v2.py - cải tiến từ bot_v1
# Cải thiện DEPTH và scoreBoard để nâng ELO

import random
import time

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 5  # tăng chiều sâu tìm kiếm

# Bảng điểm nâng cao cho vị trí
center_bonus = {(3, 3), (3, 4), (4, 3), (4, 4)}
open_file_bonus = 0.5
king_safety_penalty = -0.5


def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)

    if gs.playerWantsToPlayAsBlack:
        pass  # nếu cần đảo điểm thì có thể thêm ở đây

    turnMultiplier = 1 if gs.whiteToMove else -1
    startTime = time.time()
    timeLimit = 2

    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH,
                             -CHECKMATE, CHECKMATE,
                             turnMultiplier,
                             startTime, timeLimit)
    
    if nextMove is None and validMoves:
        nextMove = validMoves[0]

    returnQueue.put(nextMove)


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, startTime, timeLimit):
    global nextMove
    if time.time() - startTime > timeLimit:
        return 0

    if depth == 0:
        return turnMultiplier * scoreBoard(gs, turnMultiplier)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier, startTime, timeLimit)
        gs.undoMove()

        if time.time() - startTime > timeLimit:
            return 0

        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def scoreBoard(gs, turnMultiplier):
    if gs.checkmate:
        return CHECKMATE if not gs.whiteToMove else -CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for r in range(8):
        for c in range(8):
            square = gs.board[r][c]
            if square == "--":
                continue
            piece_type = square[1]
            color = square[0]

            base = pieceScore[piece_type]
            if turnMultiplier == 1:
                if color == 'w':
                    score += base
                else:
                    score -= base
            else:
                if color == 'w':
                    score -= base
                else:
                    score += base

            # bonus kiểm soát trung tâm
            if (r, c) in center_bonus:
                if (color == 'w' and turnMultiplier == 1) or (color == 'b' and turnMultiplier == -1):
                    score += 0.2
                else:
                    score -= 0.2

            # phạt cho vua đứng gần trung tâm quá sớm
            if piece_type == 'K':
                if 2 <= r <= 5 and 2 <= c <= 5:
                    score += king_safety_penalty if color == 'w' else -king_safety_penalty

    # thưởng nếu xe đứng cột mở (cột không có tốt)
    for col in range(8):
        col_pawns = [gs.board[r][col] for r in range(8) if gs.board[r][col][1:] == 'p']
        if not col_pawns:
            for r in range(8):
                square = gs.board[r][col]
                if square == 'wR':
                    score += open_file_bonus if turnMultiplier == 1 else -open_file_bonus
                elif square == 'bR':
                    score -= open_file_bonus if turnMultiplier == 1 else -open_file_bonus

    return score
