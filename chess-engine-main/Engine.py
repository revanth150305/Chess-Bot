# Engine.py
class ChessState:
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

        self.move_generators = {
            'p': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }

        self.white_turn = True
        self.move_history = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_target = ()
        self.castle_rights = CastleRights(True, True, True, True)

        self.castle_rights_log = [
            CastleRights(self.castle_rights.wks, self.castle_rights.bks,
                         self.castle_rights.wqs, self.castle_rights.bqs)
        ]

    def make_move(self, move, testing=False):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_history.append(move)
        self.white_turn = not self.white_turn

        if move.piece_moved == "wK":
            self.white_king_pos = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_pos = (move.end_row, move.end_col)

        if move.pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        if move.is_enpassant:
            self.board[move.start_row][move.end_col] = "--"

        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_target = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_target = ()

        if move.is_castling:
            if move.end_col - move.start_col == 2:  # kingside
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            elif move.end_col - move.start_col == -2:  # queenside
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        if not testing:
            self.update_castle_rights(move)

        self.castle_rights_log.append(
            CastleRights(self.castle_rights.wks, self.castle_rights.bks,
                        self.castle_rights.wqs, self.castle_rights.bqs)
        )

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.castle_rights.wqs = self.castle_rights.wks = False
        elif move.piece_moved == 'bK':
            self.castle_rights.bqs = self.castle_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.castle_rights.wqs = False
                elif move.start_col == 7:
                    self.castle_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.castle_rights.bqs = False
                elif move.start_col == 7:
                    self.castle_rights.bks = False

        if move.piece_taken == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castle_rights.wqs = False
                elif move.end_col == 7:
                    self.castle_rights.wks = False
        elif move.piece_taken == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castle_rights.bqs = False
                elif move.end_col == 7:
                    self.castle_rights.bks = False

    def undo_move(self):
        if len(self.move_history) == 0:
            return
        move = self.move_history.pop()

        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_taken
        self.white_turn = not self.white_turn


        if move.piece_moved == 'wK':
            self.white_king_pos = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.start_row, move.start_col)

        if move.pawn_promotion:
            self.board[move.start_row][move.start_col] = move.piece_moved[0] + 'p'

 
        if move.is_enpassant:
            self.board[move.end_row][move.end_col] = "--"
            self.board[move.start_row][move.end_col] = move.piece_taken


        if len(self.castle_rights_log) > 0:
            self.castle_rights_log.pop()
            if len(self.castle_rights_log) > 0:
                last = self.castle_rights_log[-1]
                self.castle_rights = CastleRights(last.wks, last.bks, last.wqs, last.bqs)


        if move.is_castling:
            if move.end_col - move.start_col == 2:  
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = "--"
            elif move.end_col - move.start_col == -2:  
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"

        self.enpassant_target = ()

        self.checkmate = False
        self.stalemate = False

    def get_legal_moves(self):
        temp_enpassant = self.enpassant_target
        temp_rights = CastleRights(self.castle_rights.wks, self.castle_rights.bks,
                                   self.castle_rights.wqs, self.castle_rights.bqs)

        moves = self.get_all_moves()
        if self.white_turn:
            self.add_castling_moves(self.white_king_pos[0], self.white_king_pos[1], moves)
        else:
            self.add_castling_moves(self.black_king_pos[0], self.black_king_pos[1], moves)


        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i], testing=True)
            self.white_turn = not self.white_turn
            if self.in_check():
                moves.remove(moves[i])
            self.white_turn = not self.white_turn
            self.undo_move()
        
        pieces_alive = [piece for row in self.board for piece in row if piece != "--"]
        if pieces_alive == ["wK", "bK"] or set(pieces_alive) == {"wK", "bK"}:
            self.stalemate = True
            self.checkmate = False
            return []

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassant_target = temp_enpassant
        self.castle_rights = temp_rights
        return moves

    def in_check(self):
        if self.white_turn:
            return self.square_threatened(self.white_king_pos[0], self.white_king_pos[1])
        else:
            return self.square_threatened(self.black_king_pos[0], self.black_king_pos[1])

    def square_threatened(self, row, col):

        original_turn = self.white_turn
        self.white_turn = not original_turn
        opponent_moves = self.get_all_moves()
        self.white_turn = original_turn
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_all_moves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == "--":
                    continue
                color = self.board[r][c][0]
                if (color == 'w' and self.white_turn) or (color == 'b' and not self.white_turn):
                    piece_type = self.board[r][c][1]
                    
                    generator = self.move_generators.get(piece_type)
                    if generator:
                        generator(r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_turn:

            if r - 1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))

                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c > 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassant_target:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant=True))
            if c < 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassant_target:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant=True))
        else:
            if r + 1 <= 7 and self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c > 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassant_target:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_enpassant=True))
            if c < 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassant_target:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_enpassant=True))

    def get_rook_moves(self, r, c, moves):
        self._slide_piece(r, c, moves, directions=[(1,0), (-1,0), (0,1), (0,-1)])

    def get_bishop_moves(self, r, c, moves):
        self._slide_piece(r, c, moves, directions=[(1,1), (-1,1), (1,-1), (-1,-1)])

    def get_queen_moves(self, r, c, moves):
        self._slide_piece(r, c, moves, directions=[(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)])

    def get_knight_moves(self, r, c, moves):
        ally = 'w' if self.white_turn else 'b'
        for dr, dc in [(-2,-1), (-1,-2), (-2,1), (-1,2), (2,1), (1,2), (2,-1), (1,-2)]:
            end_r, end_c = r+dr, c+dc
            if 0 <= end_r < 8 and 0 <= end_c < 8 and self.board[end_r][end_c][0] != ally:
                moves.append(Move((r, c), (end_r, end_c), self.board))

    def get_king_moves(self, r, c, moves):
        ally = 'w' if self.white_turn else 'b'
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == dc == 0:
                    continue
                end_r, end_c = r + dr, c + dc
                if 0 <= end_r < 8 and 0 <= end_c < 8 and self.board[end_r][end_c][0] != ally:
                    moves.append(Move((r, c), (end_r, end_c), self.board))

    def _slide_piece(self, r, c, moves, directions):
        ally = 'w' if self.white_turn else 'b'
        for dr, dc in directions:
            for step in range(1, 8):
                end_r, end_c = r + dr * step, c + dc * step
                if 0 <= end_r < 8 and 0 <= end_c < 8:
                    target = self.board[end_r][end_c]
                    if target == "--":
                        moves.append(Move((r, c), (end_r, end_c), self.board))
                    elif target[0] != ally:
                        moves.append(Move((r, c), (end_r, end_c), self.board))
                        break
                    else:
                        break
                else:
                    break

    def add_castling_moves(self, r, c, moves):
        if self.square_threatened(r, c):
            return
        if (self.white_turn and self.castle_rights.wks) or (not self.white_turn and self.castle_rights.bks):
            self._add_kingside_castle(r, c, moves)
        if (self.white_turn and self.castle_rights.wqs) or (not self.white_turn and self.castle_rights.bqs):
            self._add_queenside_castle(r, c, moves)

    def _add_kingside_castle(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_threatened(r, c+1) and not self.square_threatened(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castling=True))

    def _add_queenside_castle(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_threatened(r, c-1) and not self.square_threatened(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castling=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranks_to_rows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rows_to_ranks = {v:k for k,v in ranks_to_rows.items()}
    files_to_cols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    cols_to_files = {v:k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant=False, is_castling=False):
        self.start_row, self.start_col = start_sq
        self.end_row, self.end_col = end_sq
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_taken = board[self.end_row][self.end_col]
        self.pawn_promotion = (
            self.piece_moved == 'wp' and self.end_row == 0
        ) or (
            self.piece_moved == 'bp' and self.end_row == 7
        )
        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self.piece_taken = 'wp' if self.piece_moved == 'bp' else 'bp'
        self.is_castling = is_castling
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        return isinstance(other, Move) and self.move_id == other.move_id

    def get_notation(self):
        return self._pos_to_notation(self.start_row, self.start_col) + self._pos_to_notation(self.end_row, self.end_col)

    def _pos_to_notation(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
