#TODO:draw up uml diagram to find inefficiencies
import copy

#TODO: replacement class that will allow more memoirization
#TODO: challenge, how to check for en passent or allow move history is such a system

white_str = 'White'
black_str = 'Black'

class Board():
    def __init__(self):
        self.white_player = Player(white_str)
        self.black_player = Player(black_str)
        self.valid_move_dict = {}

    def get_valid_moves(self, white_player, black_player, turn):
        board_tuple = self.get_board_tuple(white_player, black_player)
        valid_moves = self.valid_move_dict.get((board_tuple, turn), None)

        if valid_moves is None:
            pass
        pass



    def get_board_tuple(self, white_player, black_player):
        result = []
        for i in white_player.pieces:
            result.append(i.get_position_if_alive())
        for i in black_player.pieces:
            result.append(i.get_position_if_alive())
        return tuple(result)

    def are_locations_on_board(self):
        pass

class Player():
    def __init__(self, color, *input_pieces):
        if not(input_pieces):
            self.pieces = {}
            self.color = color
            if color == 'White':
                self.king_id = 4

                self.pieces.append(Rook(0, 0, color))
                self.pieces.append(Knight(1, 0, color))
                self.pieces.append(Bishop(2, 0, color))
                self.pieces.append(Queen(3, 0, color))
                self.pieces.append(King(4, 0, color))
                self.pieces.append(Bishop(5, 0, color))
                self.pieces.append(Knight(6, 0, color))
                self.pieces.append(Rook(7, 0, color))
                self.pieces.append(Pawn(0, 1, color))
                self.pieces.append(Pawn(1, 1, color))
                self.pieces.append(Pawn(2, 1, color))
                self.pieces.append(Pawn(3, 1, color))
                self.pieces.append(Pawn(4, 1, color))
                self.pieces.append(Pawn(5, 1, color))
                self.pieces.append(Pawn(6, 1, color))
                self.pieces.append(Pawn(7, 1, color))

            elif color == 'Black':
                self.king_id = 19
                self.pieces.append(Rook(0, 7, color))
                self.pieces.append(Knight(1, 7, color))
                self.pieces.append(Bishop(2, 7, color))
                self.pieces.append(King(3, 7, color))
                self.pieces.append(Queen(4, 7, color))
                self.pieces.append(Bishop(5, 7, color))
                self.pieces.append(Knight(6, 7, color))
                self.pieces.append(Rook(7, 7, color))
                self.pieces.append(Pawn(0, 6, color))
                self.pieces.append(Pawn(1, 6, color))
                self.pieces.append(Pawn(2, 6, color))
                self.pieces.append(Pawn(3, 6, color))
                self.pieces.append(Pawn(4, 6, color))
                self.pieces.append(Pawn(5, 6, color))
                self.pieces.append(Pawn(6, 6, color))
                self.pieces.append(Pawn(7, 6, color))

            else:
                raise Exception('Invalid piece color for pawn, color is {0}'.format(color))
        else:
            self.pieces = input_pieces[0]
            self.color = color

    def get_players_possible_moves(self):
        moves = []
        for i in self.pieces.keys():
            if self.pieces[i].alive:
                moves.extend(self.pieces[i].get_possible_piece_moves())
        return moves

class MovePiece():
    def __init__(self, begin_location, end_location, other_squares_required, piece_taken_location, move_name):
        self.begin_location = begin_location
        self.end_location = end_location
        self.other_squares_required = other_squares_required
        self.piece_taken_location = piece_taken_location
        self.move_name = move_name

    def return_move_tuple(self):
        return (self.begin_location, self.end_location, self.piece_taken_location)

class Move():
    def __init__(self):
        self.moves = []

    def __init__(self, begin_location, end_location, other_squares_required, piece_taken_location, move_name):
        self.moves = []
        self.moves.append(MovePiece(begin_location, end_location, other_squares_required, piece_taken_location, move_name))

    def add_move(self, begin_location, end_location, other_squares_required, piece_taken_location, move_name):
        self.moves.append(MovePiece(begin_location, end_location, other_squares_required, piece_taken_location, move_name))

class Piece():
    #pid is unique for all pieces
    #x,y are indexes 0 to 7 of rows and column, 0,0 is the white rook queenside, pawn in front of it is 0,1
    # (0,7), (1,7), (2,7)...
    # (0,6), (1,6), (2,6)...
    # (0,5), (1,5), (2,5)...

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.alive = True
        self.name = None

    def get_possible_piece_moves(self):
        moves = []
        if not(self.alive):
            return moves

    def get_position(self):
        return (self.x, self.y)

    def get_position_if_alive(self):
        if self.alive:
            return (self.x, self.y)
        else:
            return None

    def set_position(self, x, y):
        self.x = x
        self.y = y

#TODO: add en passent
class Pawn(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Pawn'

    def get_possible_piece_moves(self):
        super().get_possible_piece_moves()
        moves = []

        if self.color == 'White':
            if self.y == 1:
                moves.append(Move((self.x, self.y), (self.x, self.y+2), [(self.x, self.y+ 1)], None, 'Pawn double move'))
            moves.append(Move((self.x, self.y), (self.x, self.y + 1), [], None, 'Pawn move'))
            moves.append(Move((self.x, self.y), (self.x + 1, self.y + 1), [], (self.x + 1, self.y + 1), 'Pawn capture'))
            moves.append(Move((self.x, self.y), (self.x - 1, self.y + 1), [], (self.x - 1, self.y + 1), 'Pawn capture'))

        elif self.color == 'Black':
            if self.y == 6:
                moves.append(Move((self.x, self.y), (self.x, self.y - 2), [(self.x, self.y - 1)], None, 'Pawn double move'))
            moves.append(Move((self.x, self.y), (self.x, self.y - 1), [], None, 'Pawn move'))
            moves.append(Move((self.x, self.y), (self.x + 1, self.y - 1), [], (self.x + 1, self.y - 1), 'Pawn capture'))
            moves.append(Move((self.x, self.y), (self.x - 1, self.y - 1), [], (self.x - 1, self.y - 1), 'Pawn capture'))
        else:
            raise Exception('Invalid piece color for pawn, color is {0}, piece_id:{1}')
        return moves

class Rook(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Rook'

    def get_possible_piece_moves(self):
        super().get_possible_piece_moves()
        moves = []

        for i in range(1,8):
            moves.append(Move((self.x, self.y), (self.x, self.y + i),
                              [(self.x, self.y + j) for j in range(1, i)],
                              (self.x, self.y + i), 'Rook move'))
            moves.append(Move((self.x, self.y), (self.x, self.y - i),
                              [(self.x, self.y - j) for j in range(1, i)],
                              (self.x, self.y - i), 'Rook move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y),
                              [(self.x + j, self.y) for j in range(1, i)],
                              (self.x + i, self.y), 'Rook move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y),
                              [(self.x - j, self.y) for j in range(1, i)],
                              (self.x - i, self.y), 'Rook move'))
        return moves

class Bishop(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Bishop'

    def get_possible_piece_moves(self):
        super().get_possible_piece_moves()
        moves = []

        for i in range(1,8):
            moves.append(Move((self.x, self.y), (self.x + i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x + i, self.y + i), 'Bishop move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x + i, self.y - i), 'Bishop move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x - i, self.y + i), 'Bishop move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x - i, self.y - i), 'Bishop move'))
        return moves

class Knight(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Knight'

    def get_possible_piece_moves(self):
        super().get_possible_piece_moves()
        moves = []
        moves.append(Move((self.x, self.y), (self.x + 1, self.y + 2), [], (self.x + 1, self.y + 2), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x + 1, self.y - 2), [], (self.x + 1, self.y - 2), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 1, self.y + 2), [], (self.x - 1, self.y + 2), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 1, self.y - 2), [], (self.x - 1, self.y - 2), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x + 2, self.y + 1), [], (self.x + 2, self.y + 1), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x + 2, self.y - 1), [], (self.x + 2, self.y - 1), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 2, self.y + 1), [], (self.x - 2, self.y + 1), 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 2, self.y - 1), [], (self.x - 2, self.y - 1), 'Knight move'))
        return moves

class King(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'King'

    def get_possible_piece_moves(self):
        super().get_possible_piece_moves()
        moves = []
        moves.append(Move((self.x, self.y), (self.x, self.y + 1),[], (self.x, self.y + 1), 'King move'))
        moves.append(Move((self.x, self.y),(self.x, self.y - 1),[], (self.x, self.y - 1),'King move'))
        moves.append(Move((self.x, self.y),(self.x - 1, self.y + 1),[], (self.x - 1, self.y + 1),'King move'))
        moves.append(Move((self.x, self.y),(self.x - 1, self.y),[], (self.x - 1, self.y),'King move'))
        moves.append(Move((self.x, self.y),(self.x - 1, self.y - 1),[], (self.x - 1, self.y - 1),'King move'))
        moves.append(Move((self.x, self.y),(self.x + 1, self.y + 1),[], (self.x + 1, self.y + 1),'King move'))
        moves.append(Move((self.x, self.y),(self.x + 1, self.y ),[], (self.x + 1, self.y ),'King move'))
        moves.append(Move((self.x, self.y),(self.x + 1, self.y - 1),[], (self.x + 1, self.y - 1),'King move'))
        return moves

class Queen(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Queen'

    def get_possible_piece_moves(self):
        super().get_possible_piece_moves()
        moves = []

        for i in range(1,8):
            moves.append(Move((self.x, self.y), (self.x + i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x + i, self.y + i), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x + i, self.y - i), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x - i, self.y + i), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x - i, self.y - i), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x, self.y + i),
                              [(self.x, self.y + j) for j in range(1, i)],
                              (self.x, self.y + i), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x, self.y - i),
                              [(self.x, self.y - j) for j in range(1, i)],
                              (self.x, self.y - i), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y),
                              [(self.x + j, self.y) for j in range(1, i)],
                              (self.x + i, self.y), 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y),
                              [(self.x - j, self.y) for j in range(1, i)],
                              (self.x - i, self.y), 'Queen move'))
        return moves


