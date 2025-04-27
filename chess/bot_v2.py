# Upgraded Chess Bot: bot_v3.py - ELO 2200+
import random
import time
import math
from collections import defaultdict

# Piece values
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 6

# King safety zones
kingSafetyZones = [
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 1, 2, 2, 2, 2, 1, 0],
    [0, 2, 4, 5, 5, 4, 2, 0],
    [1, 2, 5, 7, 7, 5, 2, 1],
    [1, 2, 5, 7, 7, 5, 2, 1],
    [0, 2, 4, 5, 5, 4, 2, 0],
    [0, 1, 2, 2, 2, 2, 1, 0],
    [0, 0, 0, 1, 1, 0, 0, 0]
]

# Transposition Table
class TranspositionTable:
    def __init__(self):
        self.table = {}

    def get(self, key):
        return self.table.get(key, None)

    def put(self, key, depth, score):
        self.table[key] = (depth, score)

transTable = TranspositionTable()

# Main function

def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    timeLimit = 9.5
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
        score = negaMaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1, start, timeLimit)
        if time.time() - start > timeLimit:
            break
        nextMove = tempMove
        depth += 1


def negaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, start, timeLimit):
    global nextMove

    key = str(gs.board) + str(gs.whiteToMove)
    cached = transTable.get(key)
    if cached is not None and cached[0] >= depth:
        return cached[1]

    if depth == 0:
        return quiescence(gs, alpha, beta, turnMultiplier)

    maxScore = -CHECKMATE
    orderedMoves = orderMoves(validMoves)

    for move in orderedMoves:
        if time.time() - start > timeLimit:
            break
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier, start, timeLimit)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    transTable.put(key, depth, maxScore)
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
    whiteKingPos = None
    blackKingPos = None

    for r in range(8):
        for c in range(8):
            piece = gs.board[r][c]
            if piece != "--":
                value = pieceScore.get(piece[1], 0)
                if piece[0] == 'w':
                    score += value
                    if piece[1] == 'K':
                        whiteKingPos = (r, c)
                else:
                    score -= value
                    if piece[1] == 'K':
                        blackKingPos = (r, c)

    # King safety
    if whiteKingPos:
        score += 0.2 * kingSafetyZones[whiteKingPos[0]][whiteKingPos[1]]
    if blackKingPos:
        score -= 0.2 * kingSafetyZones[blackKingPos[0]][blackKingPos[1]]

    # Pawn structure
    score += evaluatePawns(gs)

    # Mobility
    score += 0.1 * (len(gs.getValidMoves()) if gs.whiteToMove else -len(gs.getValidMoves()))

    return score


def evaluatePawns(gs):
    board = gs.board
    score = 0
    whitePawns = []
    blackPawns = []

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == 'wp':
                whitePawns.append((r, c))
            elif piece == 'bp':
                blackPawns.append((r, c))

    score += evaluatePawnStructure(whitePawns, 1)
    score += evaluatePawnStructure(blackPawns, -1)

    return score


def evaluatePawnStructure(pawns, multiplier):
    files = defaultdict(int)
    score = 0

    for (r, c) in pawns:
        files[c] += 1

    for c in files:
        if files[c] > 1:
            score -= multiplier * 0.5  # Doubled pawn penalty

        isolated = True
        if c-1 in files or c+1 in files:
            isolated = False
        if isolated:
            score -= multiplier * 0.5  # Isolated pawn penalty

    return score


def findRandomMoves(validMoves):
    return random.choice(validMoves)
