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
