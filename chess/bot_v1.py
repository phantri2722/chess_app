# Chess bot
import random
import time

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 2, 1, 1, 2, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, "B": bishopScores, "Q": queenScores,
                       "R": rookScores, "wp": whitePawnScores, "bp": blackPawnScores}

CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 6


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def get(self, zobrist_hash):
        return self.table.get(zobrist_hash, None)

    def put(self, zobrist_hash, depth, score):
        self.table[zobrist_hash] = (depth, score)

transTable = TranspositionTable()

# Main entry point
def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None

    timeLimit = 9.5  # Buffer to guarantee under 10s
    start = time.time()

    iterativeDeepening(gs, validMoves, start, timeLimit)

    if nextMove is None:
        nextMove = random.choice(validMoves)

    returnQueue.put(nextMove)


def iterativeDeepening(gs, validMoves, start, timeLimit):
    global nextMove
    depth = 1
    while True:
        if time.time() - start > timeLimit:
            break
        tempMove = None
        score = negaMaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1, start, timeLimit, tempMove)
        if time.time() - start > timeLimit:
            break
        nextMove = tempMove
        depth += 1


def negaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, start, timeLimit, tempMove):
    if depth == 0:
        return quiescence(gs, alpha, beta, turnMultiplier)

    maxScore = -CHECKMATE
    orderedMoves = orderMoves(validMoves)

    for move in orderedMoves:
        if time.time() - start > timeLimit:
            break
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier, start, timeLimit, tempMove)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    return maxScore


def quiescence(gs, alpha, beta, turnMultiplier):
    stand_pat = turnMultiplier * scoreBoard(gs)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    for move in gs.getValidMoves():
        if move.isCapture:
            gs.makeMove(move)
            score = -quiescence(gs, -beta, -alpha, -turnMultiplier)
            gs.undoMove()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha


def orderMoves(moves):
    captures = [m for m in moves if m.isCapture]
    nonCaptures = [m for m in moves if not m.isCapture]
    return captures + nonCaptures


def scoreBoard(gs):
    if gs.checkmate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece != "--":
                value = pieceScore.get(piece[1], 0)
                posValue = 0
                if piece[1] != "K":
                    posValue = piecePositionScores.get(piece, piecePositionScores.get(piece[1], [[0]*8]*8))[row][col]
                
                if piece[0] == 'w':
                    score += value + posValue * 0.1
                else:
                    score -= value + posValue * 0.1
    
    # Bonus for mobility
    score += 0.1 * (len(gs.getValidMoves()) if gs.whiteToMove else -len(gs.getValidMoves()))

    return score


def findRandomMoves(validMoves):
    return random.choice(validMoves)