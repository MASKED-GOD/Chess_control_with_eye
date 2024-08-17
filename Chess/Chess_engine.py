class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p':self.getPawnMoves,'R':self.getRookMoves,'B':self.getBishopMoves,'N':self.getKnightMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKinglocation =(7,4)
        self.blackKinglocation =(0,4)
        self.checkMate = False
        self.staleMate = False
        self.pins = []
        self.checks = []
        self.enpassantpossible = ()


        
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wk":
            self.whiteKinglocation =(move.endRow,move.endCol)
        elif move.pieceMoved == "bk":
            self.blackKinglocation = (move.endRow,move.endCol)
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #en passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
            
            if move.pieceMoved[1] == 'p' and abs(move.startRow- move.endRow) == 2:
                self.enpassantpossible = ((move.startRow + move.endRow)//2,move.startCol) 
            else:
                self.enpassantpossible = ()

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wk":
               self.whiteKinglocation =(move.endRow,move.endCol)
            elif move.pieceMoved == "bk":
                self.blackKinglocation = (move.endRow,move.endCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantpossible = (move.endRow,move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantpossible = ()

    def validMoves(self):
        # tempEnpassantPossible = self.enpassantpossible
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKinglocation[0]
            kingCol = self.whiteKinglocation[1]
        else:
            kingRow = self.blackKinglocation[0]
            kingCol = self.blackKinglocation[1]

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        # self.enpassantpossible = tempEnpassantPossible
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKinglocation[0],self.whiteKinglocation[1])
        else:
            return self.squareUnderAttack(self.blackKinglocation[0],self.blackKinglocation[1])
        
    def squareUnderAttack(self ,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves
    
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned =True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        # for white pawn
        if self.whiteToMove:
            if self.board[r-1][c] == '--':
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c - 1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                    elif (r-1,c-1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
                        
            if c + 1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                    elif (r-1,c+1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
                                
        # for black pawn
        else:
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                    elif (r+1,c-1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
                                   
            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                    elif (r+1,c+1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
                        
    def getRookMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned =True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1]!= 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions =((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r +d[0]*i
                endCol = c +d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol <8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))

                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break                                        
                        else:
                            break
                else:
                    break
                
    def getBishopMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned =True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0<= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]): 
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--" : 
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                else:
                    break


    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)
    
    def getKnightMoves(self,r,c,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned =True
                self.pins.remove(self.pins[i])
                break
        KnightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor ="w" if self.whiteToMove else "b"
        for m in KnightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8  and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))

                        
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        # kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKinglocation = (endRow,endCol)
                    else:
                        self.blackKinglocation = (endRow,endCol)
                    inCheck , PermissionError , checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == "w":
                        self.whiteKinglocation = (r,c)
                    else:
                        self.blackKinglocation = (r,c)

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow, startCol = self.whiteKinglocation
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow, startCol = self.blackKinglocation

        # Directions: vertical, horizontal, diagonal
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):  # Maximum distance a piece can move is 7 squares
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Check if the square is on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # First allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # Second allied piece in the line; not a pin
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # Check if the enemy piece is putting the king in check
                        # Rook (0 <= j <= 3) for straight lines
                        # Bishop (4 <= j <= 7) for diagonals
                        # Pawn (specific diagonal captures)
                        # Queen (both straight lines and diagonals)
                        # King (only one square away)
                        if (0 <= j <= 3 and type == 'R') or \
                        (4 <= j <= 7 and type == 'B') or \
                        (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                        (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # No blocking piece, so it's a check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                print(f"Check detected: King is in check by {type} at ({endRow}, {endCol})")
                            else:  # It's a pin
                                pins.append(possiblePin)
                            break
                        else:  # Other enemy piece; not a check
                            break
                    else:  # Empty square
                        continue
                else:  # Off board
                    break

        # Check for knight checks
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
                    print(f"Check detected: King is in check by Knight at ({endRow}, {endCol})")

        return inCheck, pins, checks

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board,isEnpassantMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = False
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)       
        
        # enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'


        self.moveID = self.startRow*1000 + self.startCol*100 +self.endRow*10 +self.endCol
        


    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    