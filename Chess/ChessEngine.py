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

    def make_move(self, move):
        self.board[move.endRow][move.endCol] = self.board[move.startRow][move.startCol]
        self.board[move.startRow][move.startCol] = "-"
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = self.board[move.endRow][move.endCol]
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    def get_valid_moves(self):
        return self.get_possible_moves()

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
        r, c = row + row_dir, col + col_dir
        while 0 <= r < DIMENSION and 0 <= c < DIMENSION:
            if self.board[r][c] != '-':
                if self.board[row][col][0] != self.board[r][c][0]:
                    moves.append(Move((row, col), (r, c), self.board))
                break
            else:
                moves.append(Move((row, col), (r, c), self.board))
            r += row_dir
            c += col_dir

    def check_for_piece_single(self, direction, row, col, moves):
        for d in direction:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < DIMENSION and 0 <= end_col < DIMENSION:
                if self.board[end_row][end_col] == '-' or self.board[end_row][end_col][0] != self.board[row][col][0]:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_pawn_moves(self, row, col, moves):
        if self.whiteToMove:
            if self.board[row-1][col] == '-':
                moves.append(Move((row,col), (row-1,col), self.board))
                if row == 6 and self.board[row-2][col] == '-':
                    moves.append(Move((row,col), (row-2, col), self.board))
            if 0<col and self.board[row-1][col-1][0] == 'b':
                moves.append(Move((row, col), (row - 1, col-1), self.board))
            if col<7 and self.board[row-1][col+1][0] == 'b':
                moves.append(Move((row, col), (row - 1, col+1), self.board))
        else:
            if self.board[row+1][col] == '-':
                moves.append(Move((row,col), (row+1,col), self.board))
                if row == 1 and self.board[row+2][col] == '-':
                    moves.append(Move((row,col), (row+2, col), self.board))
            if 0<col and self.board[row+1][col-1][0] == 'w':
                moves.append(Move((row, col), (row + 1, col-1), self.board))
            if col<7 and self.board[row+1][col+1][0] == 'w':
                moves.append(Move((row, col), (row + 1, col+1), self.board))

    def get_rook_moves(self, row, col, moves):
        self.check_for_piece_stream(1,0, moves, row, col)
        self.check_for_piece_stream(-1,0, moves, row, col)
        self.check_for_piece_stream(0,1, moves, row, col)
        self.check_for_piece_stream(0,-1, moves, row, col)

    def get_bishop_moves(self, row, col, moves):
        self.check_for_piece_stream(1, 1, moves, row, col)
        self.check_for_piece_stream(-1, -1, moves, row, col)
        self.check_for_piece_stream(-1, 1, moves, row, col)
        self.check_for_piece_stream(1, -1, moves, row, col)

    def get_knight_moves(self, row, col, moves):
        knight_directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        self.check_for_piece_single(knight_directions, row, col, moves)

    def get_queen_moves(self, row, col, moves):
        self.check_for_piece_stream(1, 1, moves, row, col)
        self.check_for_piece_stream(-1, -1, moves, row, col)
        self.check_for_piece_stream(-1, 1, moves, row, col)
        self.check_for_piece_stream(1, -1, moves, row, col)
        self.check_for_piece_stream(1,0, moves, row, col)
        self.check_for_piece_stream(-1,0, moves, row, col)
        self.check_for_piece_stream(0,1, moves, row, col)
        self.check_for_piece_stream(0,-1, moves, row, col)

    def get_king_moves(self, row, col, moves):
        king_directions = [(-1, -1), (1, 1), (-1, 1), (1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        self.check_for_piece_single(king_directions, row, col, moves)


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

    def __init__(self, start, end, board):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveLog = GameState().moveLog
        self.whiteToMove = GameState().whiteToMove
        self.board = GameState().board
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    #equalizing objects
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self. rows_to_ranks[r]


