import pygame as p
import Chess_engine_1

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadimages():
    pieces = ['wp', 'wN', 'wR', 'wB', 'wK', 'wQ', 'bp', 'bN', 'bR', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.image.load("Chess\\images\\" + piece + ".png")

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    gs = Chess_engine_1.GameState()
    validMoves = gs.validMoves()
    moveMade = False
    loadimages()
    running = True
    sqSelected = ()  # No square is selected initially
    playerClicks = []  # Keeps track of player clicks (two tuples: (row, col))
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) position of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):  # Deselect if the same square
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:  # After second click
                    move = Chess_engine_1.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True  
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.validMoves()
            moveMade = False

        drawGameState(screen, gs, sqSelected)  # Pass sqSelected and currentPlayer here
        clock.tick(MAX_FPS)
        p.display.flip()
def drawBoard(screen, sqSelected, currentPlayer, board):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    
    # Highlight the selected square
    if sqSelected != ():
        r, c = sqSelected
        highlightColor = p.Color("red")  # Choose your highlight color
        p.draw.rect(screen, highlightColor, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE), 4)  # Border thickness is 4

    # Highlight the squares of the pieces of the current player
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--" and piece[0] == currentPlayer:
                p.draw.rect(screen, p.Color("yellow"), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE), 2)  # Border thickness is 2

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # If not an empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawGameState(screen, gs, sqSelected):
    currentPlayer = 'w' if gs.whiteToMove else 'b'
    drawBoard(screen, sqSelected, currentPlayer, gs.board)
    drawPieces(screen, gs.board)  # No need to pass currentPlayer here

if __name__ == "__main__":
    main()