# Shaayan Syed
# shaayans
# Homework 2

import time


# ----- INPUT -----

# Helper functions for quick shifts to bitboards based on respective moves
def UR(bitboard):
    return (bitboard << 4) & borderMask
def UL(bitboard):
    return (bitboard << 5) & borderMask
def DR(bitboard):
    return (bitboard >> 5) & borderMask
def DL(bitboard):
    return (bitboard >> 4) & borderMask

# Initialize masks, bitboards, and dictionaries
borderMask = 0b11111111011111111011111111011111111
centerEvalMask1 = 0b00000111010000001010000001011100000
centerEvalMask2 = 0b00000000001100110001100110000000000
startRowMaskW = 0b00000000000000000000000000000001111
startRowMaskB = 0b11110000000000000000000000000000000
whitePieces = 0
blackPieces = 0
kingPieces = 0
bitsToPos = { 1: "g1", 2: "e1", 4: "c1", 8: "a1", 16: "h2", 32: "f2", 64: "d2", 
                128: "b2", 512: "g3", 1024: "e3", 2048: "c3", 4096: "a3", 
                8192: "h4", 16384: "f4", 32768: "d4", 65536: "b4", 262144: "g5",
                524288: "e5", 1048576: "c5", 2097152: "a5", 4194304: "h6",
                8388608: "f6", 16777216: "d6", 33554432: "b6", 134217728: "g7",
                268435456: "e7", 536870912: "c7", 1073741824: "a7", 
                2147483648: "h8", 4294967296: "f8", 8589934592: "d8",
                17179869184: "b8" }
posToBits = { "g1": 1, "e1": 2, "c1": 4, "a1": 8, "h2": 16, "f2": 32, "d2": 64, 
                "b2": 128, "g3": 512, "e3": 1024, "c3": 2048, "a3": 4096, "h4": 8192, 
                "f4": 16384, "d4": 32768, "b4": 65536,"g5": 262144, "e5": 524288,
                "c5": 1048576, "a5": 2097152, "h6": 4194304, "f6": 8388608,
                "d6": 16777216, "b6": 33554432, "g7": 134217728, "e7": 268435456,
                "c7": 536870912, "a7": 1073741824, "h8": 2147483648, "f8": 4294967296,
                "d8": 8589934592, "b8": 17179869184 }
moveToShifts = { "UR": UR, "UL": UL, "DR": DR, "DL": DL }

# Read input and place into initialized variable
gameType = ""
pieceColor = ""
timeRemaining = 0
count = 0b10000000000000000000000000000000000    # Keeps track of the pos on the board
with open("input.txt", "r") as f:
    gameType = f.readline()[:-1]
    pieceColor = f.readline()[:-1]
    timeRemaining = float(f.readline())
    

    lineCount = 1    # Is used to keep track of whether to start the pos in the row
                     # on the first column or the second
    for line in f:
        currLine = line[(lineCount % 2):-1:2]    # Only reads the board's legal pos
        for pos in currLine:
            if pos == 'b':
                blackPieces |= count
            elif pos == 'w':
                whitePieces |= count
            elif pos == 'B':
                kingPieces |= count
                blackPieces |= count
            elif pos == 'W':
                kingPieces |= count
                whitePieces |= count

            count >>= 1
        if lineCount % 2 == 0:
            count >>= 1

        lineCount += 1

# Calculate max depth for the minimax algorithm if the gametype is GAME
maxDepth = 6
try:
    f = open("calibrate.txt", 'r')
    calcTime = float(f.readline())
    if calcTime > timeRemaining / 20 or calcTime > 10.0:
        maxDepth = 2
    f.close()
except (IOError, ValueError):
    print("calibrate.txt does not exist")
    maxDepth = 3


# ----- SEARCH AND EVAL -----

# Helper function that returns the possible jump moves made by the white pieces
def whiteJump(currWhite, currBlack, currKings):
    possibleMoves = {}
    emptyPos = (~currWhite) & (~currBlack) & borderMask

    # Find the white pieces that can jump UR
    JUR = (((emptyPos >> 4) & currBlack) >> 4) & currWhite 
    if JUR:
        for i in range(0, 35):  # Go through each position in the bitboard
            indexPos = 1 << i
            if JUR & indexPos:  # Check if a white piece at this position can jump UR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JUR") # Add move to the 
                                                                 # dictionary

    # Find the white pieces that can jump UL
    JUL = (((emptyPos >> 5) & currBlack) >> 5) & currWhite
    if JUL:
        for i in range(0, 35):
            indexPos = 1 << i
            if JUL & indexPos:  # Check if a white piece at this position can jump UL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JUL")

    # Find the white king pieces that can jump DL
    KJDL = (((emptyPos << 4) & currBlack) << 4) & (currWhite & currKings)
    if KJDL:
        for i in range(0, 35):
            indexPos = 1 << i
            if KJDL & indexPos:  # Check if a white piece at this position can jump DL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JDL")

    # Find the white king pieces that can jump DR
    KJDR = (((emptyPos << 5) & currBlack) << 5) & (currWhite & currKings)
    if KJDR:
        for i in range(0, 35):
            indexPos = 1 << i
            if KJDR & indexPos:  # Check if a white piece at this position can jump DR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JDR")

    return possibleMoves

# Helper function that returns the possible jump moves made by the black pieces
def blackJump(currWhite, currBlack, currKings):
    possibleMoves = {}
    emptyPos = (~currWhite) & (~currBlack) & borderMask

    # Find the black pieces that can jump DR
    JDR = (((emptyPos << 5) & currWhite) << 5) & currBlack 
    if JDR:
        for i in range(0, 35):  # Go through each position in the bitboard
            indexPos = 1 << i
            if JDR & indexPos:  # Check if a black piece at this position can jump DR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JDR") # Add move to the 
                                                                 # dictionary

    # Find the black pieces that can jump DL
    JDL = (((emptyPos << 4) & currWhite) << 4) & currBlack
    if JDL:
        for i in range(0, 35):
            indexPos = 1 << i
            if JDL & indexPos:  # Check if a black piece at this position can jump DL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JDL")

    # Find the black king pieces that can jump UR
    KJUR = (((emptyPos >> 4) & currWhite) >> 4) & (currBlack & currKings)
    if KJUR:
        for i in range(0, 35):
            indexPos = 1 << i
            if KJUR & indexPos:  # Check if a black piece at this position can jump UR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JUR")

    # Find the black king pieces that can jump UL
    KJUL = (((emptyPos >> 5) & currWhite) >> 5) & (currBlack & currKings)
    if KJUL:
        for i in range(0, 35):
            indexPos = 1 << i
            if KJUL & indexPos:  # Check if a black piece at this position can jump UL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("JUL")

    return possibleMoves

# Recursive function for the jumpMoves function
def jumpMovesRecurse(whiteParam, blackParam, kingParam, color, chainRef, index):
    jumpFunc = ""
    currWhite = whiteParam
    currBlack = blackParam
    currKings = kingParam

    # Do the first pass to find possible jump moves
    if color == "BLACK":
        jumpFunc = blackJump
    else:
        jumpFunc = whiteJump
    currJumps = jumpFunc(currWhite, currBlack, currKings)

    # Return if there are no more possible jump moves
    if not currJumps:
        return

    if color == "BLACK":
        for key in currJumps:
            if key not in chainRef[index]:
                continue
            for move in currJumps[key]:
                if move not in chainRef[index][key]:
                    chainRef[index][key].append(move)

                # Reset the boards
                currWhite = whiteParam
                currBlack = blackParam
                currKings = kingParam

                movingBoard = posToBits[key]
                isKing = False

                # Check if the current piece is a king
                if (movingBoard & currBlack & currKings) != 0:
                    isKing = True

                # Take the black piece from its positions on the appropriate boards
                if isKing:
                    currKings ^= movingBoard

                # Shift movingBoard to the next pos based on the current jump move
                movingBoard = moveToShifts[move[1:]](movingBoard)

                # Remove the captured white piece
                if (movingBoard & currWhite & currKings) != 0:
                    currKings ^= movingBoard
                currWhite ^= movingBoard

                movingBoard = moveToShifts[move[1:]](movingBoard)

                if isKing:
                    currKings |= movingBoard
                currBlack |= movingBoard

                # Check for any future jumps and store them if applicable
                if index + 1 >= len(chainRef):
                    chainRef.append({})
                if bitsToPos[movingBoard] not in chainRef[index + 1]:
                    chainRef[index + 1][bitsToPos[movingBoard]] = []
                jumpMovesRecurse(currWhite, currBlack, currKings, color, chainRef,
                                    index + 1)
    else:
        for key in currJumps:
            if key not in chainRef[index]:
                continue
            for move in currJumps[key]:
                if move not in chainRef[index][key]:
                    chainRef[index][key].append(move)

                currWhite = whiteParam
                currBlack = blackParam
                currKings = kingParam

                movingBoard = posToBits[key]
                isKing = False

                if (movingBoard & currWhite & currKings) != 0:
                    isKing = True

                # Take the white piece from its positions on the appropriate boards
                if isKing:
                    currKings ^= movingBoard
                currWhite ^= movingBoard

                movingBoard = moveToShifts[move[1:]](movingBoard)

                # Remove the captured black piece
                if (movingBoard & currBlack & currKings) != 0:
                    currKings ^= movingBoard
                currBlack ^= movingBoard

                movingBoard = moveToShifts[move[1:]](movingBoard)

                if isKing:
                    currKings |= movingBoard
                currWhite |= movingBoard

                if index + 1 >= len(chainRef):
                    chainRef.append({})
                if bitsToPos[movingBoard] not in chainRef[index + 1]:
                    chainRef[index + 1][bitsToPos[movingBoard]] = []
                jumpMovesRecurse(currWhite, currBlack, currKings, color, chainRef,
                                    index + 1)

# Function that returns all the possible jump chains for pieces of a given color
def jumpMoves(whiteParam, blackParam, kingParam, color):
    jumpChains = []
    jumpFunc = ""
    currWhite = whiteParam
    currBlack = blackParam
    currKings = kingParam

    # Do the first pass to find possible jump moves
    if color == "BLACK":
        jumpFunc = blackJump
    else:
        jumpFunc = whiteJump
    currJumps = jumpFunc(currWhite, currBlack, currKings)
    jumpChains.append(currJumps)
    jumpChains.append({})

    # Update the current bitboards based on the jumps
    if color == "BLACK":
        for key in currJumps:
            for move in currJumps[key]:
                # Reset the boards
                currWhite = whiteParam
                currBlack = blackParam
                currKings = kingParam

                movingBoard = posToBits[key]
                isKing = False

                # Check if the current piece is a king
                if (movingBoard & currBlack & currKings) != 0:
                    isKing = True

                # Take the black piece from its positions on the appropriate boards
                if isKing:
                    currKings ^= movingBoard

                # Shift movingBoard to the next pos based on the current jump move
                movingBoard = moveToShifts[move[1:]](movingBoard)

                # Remove the captured white piece
                if (movingBoard & currWhite & currKings) != 0:
                    currKings ^= movingBoard
                currWhite ^= movingBoard

                movingBoard = moveToShifts[move[1:]](movingBoard)

                if isKing:
                    currKings |= movingBoard
                currBlack |= movingBoard

                # Check for any future jumps and store them if applicable
                if bitsToPos[movingBoard] not in jumpChains[1]:
                    jumpChains[1][bitsToPos[movingBoard]] = []
                jumpMovesRecurse(currWhite, currBlack, currKings, color, jumpChains, 1)
    else:
        for key in currJumps:
            for move in currJumps[key]:
                # Reset the boards
                currWhite = whiteParam
                currBlack = blackParam
                currKings = kingParam

                movingBoard = posToBits[key]
                isKing = False

                # Check if the current piece is a king
                if (movingBoard & currWhite & currKings) != 0:
                    isKing = True

                # Take the white piece from its positions on the appropriate boards
                if isKing:
                    currKings ^= movingBoard
                currWhite ^= movingBoard

                # Shift movingBoard to the next pos based on the current jump move
                movingBoard = moveToShifts[move[1:]](movingBoard)

                # Remove the captured white piece
                if (movingBoard & currBlack & currKings) != 0:
                    currKings ^= movingBoard
                currBlack ^= movingBoard

                movingBoard = moveToShifts[move[1:]](movingBoard)

                if isKing:
                    currKings |= movingBoard
                currWhite |= movingBoard

                if bitsToPos[movingBoard] not in jumpChains[1]:
                    jumpChains[1][bitsToPos[movingBoard]] = []
                jumpMovesRecurse(currWhite, currBlack, currKings, color, jumpChains, 1)

    # Gets rid of the empty dictionaries and keys with no associated moves
    for moves in jumpChains:
        toDel = []
        for key in moves:
            if not moves[key]:
                toDel.append(key)
        for key in toDel:
            del moves[key]
    cleanJumpChains = []
    for moves in jumpChains:
        if moves:
            cleanJumpChains.append(moves)

    return cleanJumpChains

# Helper function that returns the possible adjacent moves made by the white pieces
def whiteAdj(whiteParam, blackParam, kingParam):
    possibleMoves = {}
    emptyPos = (~whiteParam) & (~blackParam) & borderMask

    # Find the white pieces that can move UR
    EUR = (emptyPos >> 4) & whiteParam 
    if EUR:
        for i in range(0, 35):  # Go through each position in the bitboard
            indexPos = 1 << i
            if EUR & indexPos:  # Check if a white piece at this position can move UR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EUR") # Add move to the 
                                                                 # dictionary

    # Find the white pieces that can move UL
    EUL = (emptyPos >> 5) & whiteParam
    if EUL:
        for i in range(0, 35):
            indexPos = 1 << i
            if EUL & indexPos:  # Check if a white piece at this position can move UL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EUL")

    # Find the white king pieces that can move DL
    KEDL = (emptyPos << 4) & whiteParam & kingParam
    if KEDL:
        for i in range(0, 35):
            indexPos = 1 << i
            if KEDL & indexPos:  # Check if a white piece at this position can move DL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EDL")

    # Find the white king pieces that can move DR
    KEDR = (emptyPos << 5) & whiteParam & kingParam
    if KEDR:
        for i in range(0, 35):
            indexPos = 1 << i
            if KEDR & indexPos:  # Check if a white piece at this position can move DR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EDR")

    return possibleMoves

# Helper function that returns the possible adjacent moves made by the black pieces
def blackAdj(whiteParam, blackParam, kingParam):
    possibleMoves = {}
    emptyPos = (~whiteParam) & (~blackParam) & borderMask

    # Find the black pieces that can move DR
    EDR = (emptyPos << 5) & blackParam 
    if EDR:
        for i in range(0, 35):  # Go through each position in the bitboard
            indexPos = 1 << i
            if EDR & indexPos:  # Check if a black piece at this position can move DR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EDR") # Add move to the 
                                                                 # dictionary

    # Find the black pieces that can move DL
    EDL = (emptyPos << 4) & blackParam
    if EDL:
        for i in range(0, 35):
            indexPos = 1 << i
            if EDL & indexPos:  # Check if a black piece at this position can move DL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EDL")

    # Find the black king pieces that can move UR
    KEUR = (emptyPos >> 4) & blackParam & kingParam
    if KEUR:
        for i in range(0, 35):
            indexPos = 1 << i
            if KEUR & indexPos:  # Check if a black piece at this position can move UR
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EUR")

    # Find the black king pieces that can move UL
    KEUL = (emptyPos >> 5) & blackParam & kingParam
    if KEUL:
        for i in range(0, 35):
            indexPos = 1 << i
            if KEUL & indexPos:  # Check if a black piece at this position can move UL
                if bitsToPos[indexPos] not in possibleMoves:
                    possibleMoves[bitsToPos[indexPos]] = []
                possibleMoves[bitsToPos[indexPos]].append("EUL")

    return possibleMoves

# Function that returns all the possible adjascent moves for pieces of a given color
def adjMoves(whiteParam, blackParam, kingParam, color):
    if color == "BLACK":
        return blackAdj(whiteParam, blackParam, kingParam)
    else:
        return whiteAdj(whiteParam, blackParam, kingParam)

# Function that searches for the move (or series of jumps) that can be taken at this
# step by appropriate pieces
def searchStep():
    bestMove = []
    if gameType == "GAME":  # Use minimax with alpha-beta pruning and limited depth
                            # to approximate and return the best move to take
        bestMove = maxMove(whitePieces, blackPieces, kingPieces, pieceColor, 
                            float('-inf'), float('inf'), 1, "")[0]
    elif gameType == "SINGLE":  # Choose an arbitraty move and continue to output,
                                # since SINGLE gametype only cares that a move is valid
        currMoves = jumpMoves(whitePieces, blackPieces, kingPieces, pieceColor)
        if not currMoves:   # Find adj moves if there are no mandatory jump moves
            currMoves.append(adjMoves(whitePieces, blackPieces, kingPieces, pieceColor))

        # Formats the moves in currMoves by placing it in easy to read tuples
        newKey = next(iter(currMoves[0]))
        for moves in currMoves: # If currMoves is a chain of possible jumps, 
                                # get an arbitrary, but valid, series of jumps.
                                # Otherwise, gets an arbitrary adj move.
            # Add the move tuple to bestMove
            nextStep = moves.get(newKey, -1)
            if nextStep == -1:
                break
            else:
                nextStep = nextStep[0]
            bestMove.append((newKey, nextStep))

            # Find the next appropriate position based on the current move that will be
            # used in the next loop iteration (ONLY NEEDED FOR JUMP CHAINS)
            if nextStep[0] == 'J':
                newKey = bitsToPos[moveToShifts[nextStep[1:]](moveToShifts[nextStep[1:]](posToBits[newKey]))]

    return bestMove

# Heuristic function that evaluates the number of pieces on the board
def pieceCount(whiteParam, blackParam, kingParam, colorParam):
    numWhite = 0
    numBlack = 0

    # Calculates numWhite
    for bit in bin(whiteParam):
        numWhite += (1 if bit == '1' else 0)
    for bit in bin(whiteParam & kingParam):
        numWhite += (1 if bit == '1' else 0)

    # Calculates numBlack
    for bit in bin(blackParam):
        numBlack += (1 if bit == '1' else 0)
    for bit in bin(blackParam & kingParam):
        numBlack += (1 if bit == '1' else 0)

    if colorParam == "BLACK":
        return numBlack - numWhite
    else:
        return numWhite - numBlack

# Heuristic function that evaluates how close pieces are to becoming king
def offenseEval(whiteParam, blackParam, kingParam, colorParam):
    numWhite = 0
    numBlack = 0

    # Gets the board configuration in a format that has all 35 bits
    extendBitMask = 0b100000000000000000000000000000000000
    bitStringW = bin(extendBitMask | whiteParam)[3:]
    bitStringB = bin(extendBitMask | blackParam)[3:]

    topWhite = bitStringW[:18]
    bottomWhite = bitStringW[18:]
    for bit in topWhite:
        numWhite += (7 if bit == '1' else 0)
    for bit in bottomWhite:
        numWhite += (5 if bit == '1' else 0)

    topBlack = bitStringB[:18]
    bottomBlack = bitStringB[18:]
    for bit in topBlack:
        numBlack += (5 if bit == '1' else 0)
    for bit in bottomBlack:
        numBlack += (7 if bit == '1' else 0)

    if colorParam == "BLACK":
        return numBlack - numWhite
    else:
        return numWhite - numBlack

# Heuristic function that evaluates how much center control the agent has
def centerControl(whiteParam, blackParam, kingParam, colorParam):
    controlVal = 0
    currPieces = whiteParam
    if colorParam == "BLACK":
        currPieces = blackParam

    centerPieces1 = centerEvalMask1 & currPieces
    centerPieces2 = centerEvalMask2 & currPieces
    for bit in bin(centerPieces1):
        controlVal += (1 if bit == '1' else 0)
    for bit in bin(centerPieces2):
        controlVal += (3 if bit == '1' else 0)

    return controlVal

# Heuristic that counts the number of kings
def numKings(whiteParam, blackParam, kingParam, colorParam):
    kingVal = 0
    currPieces = whiteParam & kingParam
    if colorParam == "BLACK":
        currPieces = blackParam & kingParam

    for bit in bin(currPieces):
        kingVal += (1 if bit == '1' else 0)

    return kingVal

# Heuristic function that counts how many pieces are in the starting row
# (Is only effective during the starting game)
def defensiveRow(whiteParam, blackParam, kingParam, colorParam):
    defVal = 0
    currPieces = whiteParam & startRowMaskW
    if colorParam == "BLACK":
        currPieces = blackParam & startRowMaskB

    for bit in bin(currPieces):
        defVal += (1 if bit == '1' else 0)

    return defVal

# Heuristic function that evaluates the freedom of movement for the agent's pieces
def freeMovement(whiteParam, blackParam, kingParam, colorParam):
    movementVal = 0
    emptyPos = (~whiteParam) & (~blackParam) & borderMask

    DRMoves = 0
    DLMoves = 0
    URMoves = 0
    ULMoves = 0
    if colorParam == "BLACK":
        DRMoves = (emptyPos << 5) & blackParam
        DLMoves = (emptyPos << 4) & blackParam
        URMoves = (emptyPos >> 4) & blackParam & kingParam
        ULMoves = (emptyPos >> 5) & blackParam & kingParam
    else:
        URMoves = (emptyPos >> 4) & whiteParam
        ULMoves = (emptyPos >> 5) & whiteParam
        DLMoves = (emptyPos << 4) & whiteParam & kingParam
        DRMoves = (emptyPos << 5) & whiteParam & kingParam

    for bit in bin(DRMoves):
        movementVal += (1 if bit == '1' else 0)
    for bit in bin(DLMoves):
        movementVal += (1 if bit == '1' else 0)
    for bit in bin(URMoves):
        movementVal += (1 if bit == '1' else 0)
    for bit in bin(ULMoves):
        movementVal += (1 if bit == '1' else 0)

    return movementVal

# Evaluation function for checkers
def eval(whiteParam, blackParam, kingParam, colorParam):
    weights = [10, 8, 7, 20, 10, 9]
    PCVal = pieceCount(whiteParam, blackParam, kingParam, colorParam)
    OEVal = offenseEval(whiteParam, blackParam, kingParam, colorParam)
    CCVal = centerControl(whiteParam, blackParam, kingParam, colorParam)
    NKVal = numKings(whiteParam, blackParam, kingParam, colorParam)
    DRVal = defensiveRow(whiteParam, blackParam, kingParam, colorParam)
    FMVal = freeMovement(whiteParam, blackParam, kingParam, colorParam)

    evalVal = (weights[0] * PCVal) + (weights[1] * OEVal) + (weights[2] * CCVal) +\
                (weights[3] * NKVal) + (weights[4] * DRVal) + (weights[5] * FMVal)
    return evalVal

# Helper function used by the successors function to find configuration of a board following 
# a series of jump moves
def jumpRecurse(whiteParam, blackParam, kingParam, colorParam, index, currMoves, 
                boardListRef, key, moveList, resultMoveList):
    if index >= len(currMoves):
        resultMoveList.append(moveList.copy())
        boardListRef.append([whiteParam, blackParam, kingParam])
        return
    elif key not in currMoves[index]:
        resultMoveList.append(moveList.copy())
        boardListRef.append([whiteParam, blackParam, kingParam])
        return
    
    for move in currMoves[index][key]:
        newWhiteBoard = whiteParam
        newBlackBoard = blackParam
        newKingBoard = kingParam

        if colorParam == "BLACK":
            blackPiece = posToBits[key]
            newBlackBoard ^= blackPiece
            firstShift = moveToShifts[move[1:]](blackPiece)
            newBlackBoard ^= moveToShifts[move[1:]](firstShift)

            if newKingBoard & firstShift & newWhiteBoard != 0:
                newKingBoard ^= firstShift
            newWhiteBoard ^= firstShift

            if blackPiece & newKingBoard != 0:
                newKingBoard ^= blackPiece
                newKingBoard ^= moveToShifts[move[1:]](firstShift)
        else:
            whitePiece = posToBits[key]
            newWhiteBoard ^= whitePiece
            firstShift = moveToShifts[move[1:]](whitePiece)
            newWhiteBoard ^= moveToShifts[move[1:]](firstShift)

            if newKingBoard & firstShift & newBlackBoard != 0:
                newKingBoard ^= firstShift
            newBlackBoard ^= firstShift

            if whitePiece & newKingBoard != 0:
                newKingBoard ^= whitePiece
                newKingBoard ^= moveToShifts[move[1:]](firstShift)

        newMoveList = moveList.copy()
        newMoveList.append((key, move))
        newKey = bitsToPos[moveToShifts[move[1:]](moveToShifts[move[1:]](posToBits[key]))]
        jumpRecurse(newWhiteBoard, newBlackBoard, newKingBoard, colorParam, index + 1, 
                    currMoves, boardListRef, newKey, newMoveList, resultMoveList)  

# Helper function that gets the possible moves and successor boards for a given
# board arrangement
def successors(whiteParam, blackParam, kingParam, colorParam):
    currMoves = jumpMoves(whiteParam, blackParam, kingParam, colorParam)
    if not currMoves:
        currMoves.append(adjMoves(whiteParam, blackParam, kingParam, colorParam))

    # Initialize successorBoards and first check if there aren't any valid moves
    successorBoards = []
    correspondingMoves = []
    if not currMoves:
        return (correspondingMoves, successorBoards)
    elif not currMoves[0]:
        return (correspondingMoves, successorBoards)

    # Find successors if there are mandatory jump moves to be made
    if currMoves[0][next(iter(currMoves[0]))][0][0] == "J":
        resultBoards = []
        resultMoveList = []
        for key in currMoves[0]:
            jumpRecurse(whiteParam, blackParam, kingParam, colorParam, 0, 
                        currMoves, resultBoards, key, [], resultMoveList)
        for i in range(0, len(resultBoards)):
            successorBoards.append(resultBoards[i])
            correspondingMoves.append(resultMoveList[i])

        return (correspondingMoves, successorBoards)

    # Otherwise, find successors based on the adj moves in currMoves
    for key in currMoves[0]:
        for move in currMoves[0][key]:
            newWhiteBoard = whiteParam
            newBlackBoard = blackParam
            newKingBoard = kingParam

            if colorParam == "BLACK":
                blackPiece = posToBits[key]
                newBlackBoard ^= blackPiece
                newBlackBoard ^= moveToShifts[move[1:]](blackPiece)

                if blackPiece & newKingBoard != 0:
                    newKingBoard ^= blackPiece
                    newKingBoard ^= moveToShifts[move[1:]](blackPiece)

            else:
                whitePiece = posToBits[key]
                newWhiteBoard ^= whitePiece
                newWhiteBoard ^= moveToShifts[move[1:]](whitePiece)

                if whitePiece & newKingBoard != 0:
                    newKingBoard ^= whitePiece
                    newKingBoard ^= moveToShifts[move[1:]](whitePiece)

            successorBoards.append([newWhiteBoard, newBlackBoard, newKingBoard])
            correspondingMoves.append([(key, move)])

    return (correspondingMoves, successorBoards)

# Max function for the minimax algorithm that does alpha-beta pruning
def maxMove(whiteParam, blackParam, kingParam, colorParam, alpha, beta, depth, firstMove):
    # Tests for terminal states
    if depth >= maxDepth:   # If the max depth has been reached
        return (firstMove, eval(whiteParam, blackParam, kingParam, pieceColor))
    elif whiteParam == 0:   # If the white pieces have lost
        if colorParam == "WHITE":
            return (firstMove, -100000)
        return (firstMove, 100000)
    elif blackParam == 0:   # If the black pieces have lost
        if colorParam == "BLACK":
            return (firstMove, -100000)
        return (firstMove, 100000)

    v = ([], float('-inf'))
    newAlpha = alpha
    nextColor = "BLACK" # Change piece color after this hypothetical turn is over
    if colorParam == "BLACK":
        nextColor = "WHITE"
    successorList = successors(whiteParam, blackParam, kingParam, colorParam)
    for i in range(0, len(successorList[1])):   # Iterate through successors
        # If the first possible move has not been saved, store it
        # Else, pass it as a parameter through the recursion
        lastMove = firstMove
        if not lastMove:
            lastMove = successorList[0][i]
        minResult = minMove(successorList[1][i][0], successorList[1][i][1], 
                            successorList[1][i][2], nextColor, alpha, beta, 
                            depth + 1, lastMove)

        if v[1] < minResult[1]:
            v = minResult
        if v[1] >= beta:
            return v
        newAlpha = max(newAlpha, v[1])

    return v

# Min function for the minimax algorithm that does alpha-beta pruning
def minMove(whiteParam, blackParam, kingParam, colorParam, alpha, beta, depth, firstMove):
    # Tests for terminal states
    if depth >= maxDepth:
        return (firstMove, eval(whiteParam, blackParam, kingParam, colorParam))
    elif whiteParam == 0:
        if colorParam == "WHITE":
            return (firstMove, -100000)
        return (firstMove, 100000)
    elif blackParam == 0:
        if colorParam == "BLACK":
            return (firstMove, -100000)
        return (firstMove, 100000)

    v = ([], float('inf'))
    newBeta = beta
    nextColor = "BLACK"
    if colorParam == "BLACK":
        nextColor = "WHITE"
    successorList = successors(whiteParam, blackParam, kingParam, colorParam)
    for i in range(0, len(successorList[1])):   # Iterate through successors
        # If the first possible move has not been saved, store it
        # Else, pass it as a parameter through the recursion
        lastMove = firstMove
        if not lastMove:
            lastMove = successorList[0][i]
        maxResult = maxMove(successorList[1][i][0], successorList[1][i][1], 
                            successorList[1][i][2], nextColor, alpha, beta, 
                            depth + 1, lastMove)

        if maxResult[1] < v[1]:
            v = maxResult
        if v[1] <= alpha:
            return v
        newBeta = min(newBeta, v[1])

    return v


# ----- OUTPUT -----

moves = searchStep()
with open("output.txt", "w") as f:
    for move in moves:
        output = move[1][0] + " " + move[0] + " "
        nextPos = moveToShifts[move[1][1:]](posToBits[move[0]])
        if move[1][0] == 'J':
            nextPos = moveToShifts[move[1][1:]](nextPos)
        output += bitsToPos[nextPos]

        if move != moves[-1]:
            output += "\n"

        f.write(output)
