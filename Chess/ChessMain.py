# Main driver file. Handles user input and display current GameState object

import pygame as p
from const import *
from Chess import ChessEngine

# Load images - to be done only once to prevent lag
def load_images():
    pieces = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wp', "bR", "bN", "bB", "bQ", "bK", "bp"]
    for i in pieces:
        IMAGES[i] = p.transform.scale(p.image.load('images/' + i + '.png'), (SQSIZE, SQSIZE))

# Main Driver. Handle input and updates graphics
def main():
    p.init()
    load_images()
    screen = p.display.set_mode((HEIGHT, WIDTH))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game = ChessEngine.GameState()
    valid_moves = game.get_valid_moves()
    move_made = False
    running = True
    main.sq_selected, main.player_clicks = (), []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQSIZE
                row = location[1] // SQSIZE
                if main.sq_selected == (row, col):
                    main.sq_selected, main.player_clicks = (), []
                else:
                    main.sq_selected = (row, col)
                    main.player_clicks.append(main.sq_selected)
                if len(main.player_clicks) == 2:
                    move = ChessEngine.Move(main.player_clicks[0], main.player_clicks[1], game.board)
                    print(move.get_chess_notation())
                    if move in valid_moves:
                        game.make_move(move)
                        move_made = True
                    main.sq_selected, main.player_clicks = (), []

            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    game.undo_move()
                    move_made = True
                if e.key == p.K_e:
                    running = False

        if move_made:
            valid_moves = game.get_valid_moves()
            move_made = False

        clock.tick(MAX_FPS)
        p.display.flip()
        draw_game_state(screen, game)

def draw_game_state(screen, game):
    draw_board(screen)
    draw_pieces(screen, game.board)

def draw_board(screen):
    colours = [p.Color("#EEEED2"), p.Color("#769656")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r+c)%2)]
            p.draw.rect(screen, colour, p.Rect(c*SQSIZE, r*SQSIZE, SQSIZE, SQSIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "-":
                screen.blit(IMAGES[piece], p.Rect(c*SQSIZE, r*SQSIZE, SQSIZE, SQSIZE))

if __name__ == "__main__":
    main()