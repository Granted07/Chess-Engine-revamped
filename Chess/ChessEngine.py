# Stores all info about the current state of the chess game.
# Also determines the valid moves. Keeps a move log.

from const import *

class GameState:
    def __init__(self):

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ['-', '-', '-', '-', '-', '-', '-', '-', ],
            ['-', '-', '-', '-', '-', '-', '-', '-', ],
            ['-', '-', '-', '-', '-', '-', '-', '-', ],
            ['-', '-', '-', '-', '-', '-', '-', '-', ],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.pins = []
        self.checks = []
        self.in_check = False
        self.enpassant_possible = ()

    def make_move(self, move):
        self.board[move.endRow][move.endCol] = self.board[move.startRow][move.startCol]
        self.board[move.startRow][move.startCol] = "-"
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.white_king_loc = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.black_king_loc = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '-'

        if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
            self.enpassant_possible = ((move.startRow + move.endRow)//2 , move.endCol)
            print("Enpassant moves: ", self.enpassant_possible)
        else:
            self.enpassant_possible = ()


    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = self.board[move.endRow][move.endCol]
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.white_king_loc = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.black_king_loc = (move.startRow, move.startCol)
            if move.isEnpassant:
                self.board[move.endRow][move.endCol] = '-'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassant_possible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
                self.enpassant_possible = ()

    def get_valid_moves(self):
        temp_enpassant_possible = self.enpassant_possible
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        if self.in_check:
            if len(self.checks) == 1:
                moves = self.get_possible_moves()
                check_row, check_col = self.checks[0][0], self.checks[0][1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + self.checks[0][2] * i, king_col + self.checks[0][3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_possible_moves()

        self.enpassant_possible = temp_enpassant_possible
        return moves

    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opp_moves = self.get_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in opp_moves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def get_possible_moves(self):
        moves = []
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.get_pawn_moves(row, col, moves)
                    elif piece == 'R':
                        self.get_rook_moves(row, col, moves)
                    elif piece == 'B':
                        self.get_bishop_moves(row, col, moves)
                    elif piece == 'N':
                        self.get_knight_moves(row, col, moves)
                    elif piece == 'K':
                        self.get_king_moves(row, col, moves)
                    elif piece == 'Q':
                        self.get_queen_moves(row, col, moves)
        return moves

    def check_for_piece_stream(self, row_dir, col_dir, moves, row, col):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                break
        r, c = row + row_dir, col + col_dir
        while 0 <= r < DIMENSION and 0 <= c < DIMENSION:
            if self.board[r][c] != '-':
                if not piece_pinned or pin_direction == (row_dir, col_dir) or pin_direction == (-row_dir, -col_dir):
                    if self.board[row][col][0] != self.board[r][c][0]:
                        moves.append(Move((row, col), (r, c), self.board))
                    break
            else:
                if not piece_pinned or pin_direction == (row_dir, col_dir) or pin_direction == (-row_dir, -col_dir):
                    moves.append(Move((row, col), (r, c), self.board))
            r += row_dir
            c += col_dir

    def check_for_piece_single(self, direction, row, col, moves, pin_or_check=False):
        for d in direction:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < DIMENSION and 0 <= end_col < DIMENSION:
                if self.board[row][col][1] == 'K':
                    ally_color = self.board[row][col][0]
                    if ally_color == 'w':
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        if self.board[end_row][end_col] == '-' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally_color == 'w':
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)

                if not pin_or_check and self.board[row][col][1] != 'K':
                    if self.board[end_row][end_col] == '-' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[row-1][col] == '-':
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row,col), (row-1,col), self.board))
                    if row == 6 and self.board[row-2][col] == '-':
                        moves.append(Move((row,col), (row-2, col), self.board))
            if 0<col:
                if self.board[row-1][col-1][0] == 'b' and not (piece_pinned or pin_direction == (-1, -1)):
                    moves.append(Move((row, col), (row - 1, col-1), self.board))
                elif (row-1 , col-1) == self.enpassant_possible:
                    print("EnPassant move")
                    moves.append(Move((row, col), (row - 1, col-1), self.board), isEnpassantMove=True)
            if col<7:
                if self.board[row-1][col+1][0] == 'b' and not (piece_pinned or pin_direction == (-1, +1)):
                    moves.append(Move((row, col), (row - 1, col+1), self.board))
                elif (row-1 , col-1) == self.enpassant_possible:
                    print("EnPassant move")
                    moves.append(Move((row, col), (row - 1, col+1), self.board), isEnpassantMove=True)

        else:
            if self.board[row+1][col] == '-':
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row,col), (row+1,col), self.board))
                    if row == 1 and self.board[row+2][col] == '-':
                            moves.append(Move((row,col), (row+2, col), self.board))
            if 0<col:
                if self.board[row+1][col-1][0] == 'w' and not (piece_pinned or pin_direction == (1, -1)):
                    moves.append(Move((row, col), (row + 1, col-1), self.board))
                elif (row+1 , col-1) == self.enpassant_possible:
                    print("EnPassant move")
                    moves.append(Move((row, col), (row + 1, col-1), self.board), isEnpassantMove=True)
            if col<7:
                if self.board[row+1][col+1][0] == 'w' and not (piece_pinned or pin_direction == (1, 1 )):
                    moves.append(Move((row, col), (row + 1, col+1), self.board))
                elif (row-1 , col-1) == self.enpassant_possible:
                    print("EnPassant move")
                    moves.append(Move((row, col), (row + 1, col+1), self.board), isEnpassantMove=True)

    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                    -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "-":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "-":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        ally_color = "w" if self.whiteToMove else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_queen_moves(self, row, col, moves):
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    if ally_color == "w":
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally_color == "w":
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)


class Move:
    # Move Maps
    ranks_to_rows = {
        "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1,
        "8": 0, "9": -1, "0": -2
    }
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {
        "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7
    }
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start, end, board, isEnpassantMove=False):

        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveLog = GameState().moveLog
        self.whiteToMove = GameState().whiteToMove
        self.board = GameState().board

        self.isPawnPromotion = ((self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7))

        # self.isEnpassant = ((self.pieceMoved[1] == 'p') and ((self.endRow, self.endCol) == enpassant_possible))
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    #equalizing objects
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        return (self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol), [(self.startRow, self.startCol), (self.endRow, self.endCol)])

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self. rows_to_ranks[r]


