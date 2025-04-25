# bot_v3.py - Bot tối ưu hướng tới ELO 2200+

import random
import time

pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 6

# Ưu tiên kiểm soát trung tâm, an toàn vua, liên kết tốt...
centerSquares = [(3, 3), (3, 4), (4, 3), (4, 4)]

# Move ordering helpers
piecePriority = {"K": 0, "p": 1, "N": 2, "B": 3, "R": 4, "Q": 5}


transposition_table = {}

def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)

    turnMultiplier = 1 if gs.whiteToMove else -1
    startTime = time.time()
    timeLimit = 2

    iterativeDeepening(gs, validMoves, turnMultiplier, startTime, timeLimit)
    if nextMove is None and validMoves:
        nextMove = validMoves[0]
    returnQueue.put(nextMove)


def iterativeDeepening(gs, validMoves, turnMultiplier, startTime, timeLimit):
    global nextMove
    for depth in range(2, MAX_DEPTH + 1):
        bestMoveThisDepth = None
        maxScore = -CHECKMATE

        def negaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
            nonlocal bestMoveThisDepth, maxScore
            if time.time() - startTime > timeLimit:
                return 0

            boardHash = str(gs.board) + str(gs.whiteToMove)
            if boardHash in transposition_table and transposition_table[boardHash]["depth"] >= depth:
                return transposition_table[boardHash]["score"]

            if depth == 0:
                return turnMultiplier * scoreBoard(gs)

            localMax = -CHECKMATE
            orderedMoves = orderMoves(validMoves)

            for move in orderedMoves:
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()
                score = -negaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
                gs.undoMove()

                if time.time() - startTime > timeLimit:
                    break

                if score > localMax:
                    localMax = score
                    if depth == MAX_DEPTH or localMax > maxScore:
                        bestMoveThisDepth = move
                        maxScore = localMax

                alpha = max(alpha, localMax)
                if alpha >= beta:
                    break

            transposition_table[boardHash] = {"score": localMax, "depth": depth}
            return localMax

        negaMaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, turnMultiplier)

        if bestMoveThisDepth is not None:
            nextMove = bestMoveThisDepth
        if time.time() - startTime > timeLimit:
            break




def scoreBoard(gs):
    if gs.checkmate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece == "--":
                continue
            value = pieceScore.get(piece[1], 0)
            sign = 1 if piece[0] == 'w' else -1

            # Thêm điểm cho kiểm soát trung tâm
            if (r, c) in centerSquares:
                value += 20

            # Thêm điểm cho vị trí an toàn vua (góc)
            if piece[1] == 'K' and (r in [0, 7] and c in [0, 7]):
                value += 30

            score += value * sign
    return score

def orderMoves(moves):
    # Ưu tiên bắt quân giá trị cao bằng quân giá trị thấp
    def moveScore(move):
        score = 0
        if move.pieceCaptured != "--":
            score += 10 * pieceScore.get(move.pieceCaptured[1], 0) - pieceScore.get(move.pieceMoved[1], 0)
        score += piecePriority.get(move.pieceMoved[1], 0)
        return -score  # sắp xếp giảm dần

    return sorted(moves, key=moveScore)
