#TODO: add casteling
#TODO: add enpassant

import copy

white_color_str = 'White'
black_color_str = 'Black'

checkmate_code = 1
draw_code = 2
continue_code = 3

class Board():
    def __init__(self):
        self.reset_players()
        self.reset_dicts()

    def analyze_round_and_get_valid_moves(self, current_player_color):
        self.assert_kings_are_alive()
        self.update_pawns()
        board_tuple = self.get_board_tuple(self.white_player, self.black_player)
        saved_result = self.anayze_round_dict.get((board_tuple, current_player_color), None)

        if saved_result is not None:
            return saved_result
        else:
            result = None
            valid_moves = self.get_valid_moves(self.white_player, self.black_player, current_player_color)
            if self.is_checkmate(valid_moves, self.white_player, self.black_player, current_player_color):
                result = [checkmate_code, []]
            elif self.is_draw(valid_moves):
                result =  [draw_code, []]
            else:
                result = [continue_code, valid_moves]
            self.anayze_round_dict[(board_tuple, current_player_color)] = result

            return result

    def analyze_round_and_get_checkmate_moves(self, current_player_color):
        self.assert_kings_are_alive()
        board_tuple = self.get_board_tuple(self.white_player, self.black_player)
        saved_result = self.anayze_round_dict.get((board_tuple, current_player_color), None)

        if saved_result is not None:
            return saved_result
        else:
            result = None
            valid_moves = self.get_valid_next_move_checkmate_moves(self.white_player, self.black_player, current_player_color)
            if self.is_checkmate(valid_moves, self.white_player, self.black_player, current_player_color):
                result = [checkmate_code, []]
            elif self.is_draw(valid_moves):
                result =  [draw_code, []]
            else:
                result = [continue_code, valid_moves]
            self.anayze_round_dict[(board_tuple, current_player_color)] = result
            return result

    def analyze_round_and_get_nn(self, color):
        valid_moves  = self.get_board_tuple_for_each_move(color)
        move_data_list = [i[0] for i in valid_moves]
        if self.is_checkmate(move_data_list, self.white_player, self.black_player, color):
            result = [checkmate_code, valid_moves]
        elif self.is_draw(move_data_list):
            result = [draw_code, valid_moves]
        else:
            result = [continue_code, valid_moves]
        return result

    #this gets all posible moves and filters out illegal moves
    #prevent_self_check can be set to false to return threatened pieces even if the move would put the movign player in check, this checks threatening not posiible moves
    def get_valid_moves(self, white_player, black_player, current_player_color, prevent_self_check = True):
        board_tuple = self.get_board_tuple(white_player, black_player)
        saved_valid_moves = self.valid_move_dict.get((board_tuple, current_player_color), None)
        current_player = self.get_current_player(white_player, black_player, current_player_color)
        current_opponent = self.get_current_opponent(white_player, black_player, current_player_color)

        square_available_dict = {}
        get_square_content_dict = {}
        all_possible_moves = current_player.get_players_possible_moves()
        valid_moves = []

        for m in all_possible_moves:
            move_valid = True
            for m_p in m.move_portions:

                #check that all locations are on board
                if not(self.are_locations_on_board(m_p.end_location, m_p.piece_taken_location, m_p.required_squares)):
                    move_valid = False
                    break

                #check that all locations are empty or available
                if not(self.are_squares_available(m_p.end_location, m_p.piece_taken_location, m_p.required_squares, square_available_dict)):
                    move_valid = False
                    break

                #check that the target location is valid
                if not(self.is_taken_location_valid(white_player, black_player, current_player_color, m_p.piece_taken_location)):
                    move_valid = False
                    break

                if not(self.is_move_type_valid(current_player, m_p, get_square_content_dict)):
                    move_valid = False
                    break

            if move_valid and prevent_self_check and self.is_in_check_after_move(white_player, black_player, current_player_color,m.get_move_tuple()):
                move_valid = False

            if move_valid:
                valid_moves.append(m.get_move_tuple())

        self.valid_move_dict[(board_tuple, current_player_color)] = valid_moves
        return valid_moves

    def shrink_move_data(self, moves):
        small_moves = []
        for m in moves:
            small_moves.append(m.get_move_tuple())
        return small_moves

    def get_board_tuple(self, white_player, black_player):
        result = []
        w_pieces = sorted(white_player.pieces,  key=lambda x: x.p_id, reverse=True)
        b_pieces = sorted(black_player.pieces,  key=lambda x: x.p_id, reverse=True)
        for i in w_pieces:
            result.append(i.get_position_if_alive())
        for i in b_pieces:
            result.append(i.get_position_if_alive())
        return tuple(result)

    def get_board_tuple_for_each_move(self, color):
        moves = self.get_valid_moves(self.white_player, self.black_player, color, prevent_self_check = True)
        results = []
        for m in moves:
            white_copy, black_copy, in_check = self.execute_move(self.white_player, self.black_player, color, m, in_place=False)
            results.append([m, self.get_board_tuple(white_copy, black_copy), None, None])
        return results

    #check if in check after a move
    def is_in_check_after_move(self, white_player, black_player, current_color, move):
        white_copy, black_copy, in_check = self.execute_move(white_player, black_player, current_color, move, in_place=False)
        saved_result = in_check or self.is_player_in_check(white_copy, black_copy, current_color)
        return saved_result


    #checks if the current players king is threatened
    #gets all valid threats from opponent
    def is_player_in_check(self, white_player, black_player, current_player_color):
        board_tuple = self.get_board_tuple(white_player, black_player)
        saved_solution = self.is_in_check_dict.get((board_tuple, current_player_color), None)
        if saved_solution is None:
            current_player = self.get_current_player(white_player, black_player, current_player_color)
            current_opponent = self.get_current_opponent(white_player, black_player, current_player_color)
            opponent_moves = self.get_valid_moves( white_player, black_player, self.get_opposite_color(current_player_color), prevent_self_check = False)
            in_check = False
            for m in opponent_moves:
                for m_p in m:
                    if m_p[2] == current_player.king.get_position_if_alive():
                        in_check = True
                        break
                if in_check:
                    break
            self.is_in_check_dict[(board_tuple, current_player_color)] = in_check
            return in_check
        else:
            return saved_solution

    #this method assumes you already checked for checkmate
    def is_draw(self, valid_moves):
        if len(valid_moves) == 0 or (self.white_player.number_of_living_pieces() <= 1 and self.black_player.number_of_living_pieces() <= 1):
            return True
        else:
            return False

    def get_valid_next_move_checkmate_moves(self, white_player, black_player, current_player_color):
        valid_moves = self.get_valid_moves(white_player, black_player, current_player_color)
        checkmate_moves = []
        for i in valid_moves:
            if self.is_in_checkmate_after_move(white_player, black_player, current_player_color, i):
                checkmate_moves.append(i)
        print('checkmate_moves:',checkmate_moves)
        if len(checkmate_moves) >= 1:
            return checkmate_moves
        else:
            return valid_moves

    def is_in_checkmate_after_move(self, white_player, black_player, current_color, move):
        white_copy, black_copy, in_check = self.execute_move(white_player, black_player, current_color, move, in_place=False)
        opponent_valid_moves = self.get_valid_moves(white_player, black_player, self.get_opposite_color(current_color))
        saved_result = self.is_checkmate(opponent_valid_moves , white_copy, black_copy, self.get_opposite_color(current_color))
        return  saved_result

    def is_checkmate(self, valid_moves, white_player, black_player, current_player_color):
        if len(valid_moves) == 0 and self.is_player_in_check(white_player, black_player, current_player_color):
            return True
        return False

    #check if move type is valid
    def is_move_type_valid(self, current_player, m_p, get_square_content_dict):
        if m_p.move_name == 'Pawn capture':
            saved_square = self.get_square_content(m_p.piece_taken_location, get_square_content_dict)
            if saved_square is None:
                return False
            if saved_square.color == current_player:
                return False
        return True

    #check if taken square is not occupied by same team
    def is_taken_location_valid(self, white_player, black_player, current_player_color, location):
        if location is None:
            return True
        current_player  = self.get_current_player(white_player, black_player, current_player_color)
        for i in current_player.pieces:
            if i.get_position_if_alive() == location:
                return False
        return True

    #check if squares required are available
    def are_squares_available(self, end_location, piece_taken_location, required_squares, square_available_dict):
        for i in required_squares:
            if i != piece_taken_location:
                if not(self.is_square_available(i, square_availability_dict = square_available_dict)):
                    return False
        if end_location != piece_taken_location:
            if not(self.is_square_available(end_location, square_availability_dict = square_available_dict)):
                return False
        return True

    #checks if square content is free
    def is_square_available(self, position, square_availability_dict = None):
        if square_availability_dict is None:
            for i in self.white_player.pieces:
                if i.get_position_if_alive() == position:
                    return False
            for i in self.black_player.pieces:
                if i.get_position_if_alive() == position:
                    return False
            return True
        else:
            saved_result = square_availability_dict.get(position, None)
            if saved_result is None:
                for i in self.white_player.pieces:
                    if i.get_position_if_alive() == position:
                        square_availability_dict[position] = False
                        return False
                for i in self.black_player.pieces:
                    if i.get_position_if_alive() == position:
                        square_availability_dict[position] = False
                        return False
                return True
            else:
                return saved_result

    #check for location on board using global dict
    def are_locations_on_board(self, end_location, piece_taken_location, required_squares):
        if not(self.is_location_on_board(end_location)) or not(self.is_location_on_board(piece_taken_location)):
            return False
        for i in required_squares:
            if not(self.is_location_on_board(i)):
                return False
        return True

    def is_location_on_board(self, pos):
        return self.is_on_board_dict.setdefault(pos, pos is None or (pos[0] >= 0 and pos[0] <= 7 and pos[1] >= 0 and pos[1] <= 7))

    def execute_move(self, white_player, black_player, current_player_color, move, in_place=True):
        if not(in_place):
            white_player = copy.deepcopy(white_player)
            black_player = copy.deepcopy(black_player)
        in_check = False
        for m_p in move:
            #print('execute players:', white_player, black_player)
            capturing_piece = self.get_square_content(m_p[0], white_player=white_player, black_player=black_player)
            captured_piece = self.get_square_content(m_p[2], white_player=white_player, black_player=black_player)
            if captured_piece is not None and (captured_piece.p_id == 4 or captured_piece.p_id == 19):
                in_check = True

            if captured_piece is not None and capturing_piece.p_id != captured_piece.p_id:
                captured_piece.capture()
            self.get_square_content(m_p[0], white_player=white_player, black_player=black_player).set_position(m_p[1][0], m_p[1][1])
        return white_player, black_player, in_check


    #utility methods
    def get_square_content(self, position, white_player = None, black_player = None, square_availability_dict = None):
        if white_player is None or black_player is None:
            white_player = self.white_player
            black_player = self.black_player

        if square_availability_dict is None:
            for i in white_player.pieces:
                if i.get_position_if_alive() == position:
                    return i
            for i in black_player.pieces:
                if i.get_position_if_alive() == position:
                    return i
            return None

        else:
            saved_result = square_availability_dict.get(position, None)
            if saved_result is None:
                for i in white_player.pieces:
                    if i.get_position_if_alive() == position:
                        square_availability_dict[position] = i
                        return i
                for i in black_player.pieces:
                    if i.get_position_if_alive() == position:
                        square_availability_dict[position] = i
                        return i
                square_availability_dict[position] = None
                return None
            else:
                return saved_result

    def get_current_player(self, white_player, black_player, current_player_color):
        if white_player.is_color(current_player_color):
            return white_player
        else:
            return black_player

    def get_current_opponent(self, white_player, black_player, current_player_color):
        if not(white_player.is_color(current_player_color)):
            return white_player
        else:
            return black_player

    def get_opposite_color(self, color):
        if color == white_color_str:
            return black_color_str
        if color == black_color_str:
            return white_color_str

    def get_player_by_color(self, color):
        if color == white_color_str:
            return self.white_player
        if color == black_color_str:
            return self.black_player

    def reset_players(self):
        self.white_player = Player(white_color_str)
        self.black_player = Player(black_color_str)

    def reset_dicts(self):
        self.valid_move_dict = {}
        self.is_on_board_dict = {}
        self.is_in_check_dict = {}
        self.anayze_round_dict = {}

    def assert_kings_are_alive(self):
        if not(self.white_player.king.alive and self.black_player.king.alive):
            raise Exception('Kings are dead:' + self.white_player.king.__dict__ + self.black_player.king.__dict__ )

    def update_pawns(self):
        for i in range(len(self.white_player.pieces)):
            if self.white_player.pieces[i].name == 'Pawn' and self.white_player.pieces[i].y == 7:
                self.white_player.pieces[i] = Queen(self.white_player.pieces[i].x, self.white_player.pieces[i].y, self.white_player.pieces[i].color, i)
        for i in range(len(self.black_player.pieces)):
            if self.black_player.pieces[i].name == 'Pawn' and self.black_player.pieces[i].y == 0:
                self.black_player.pieces[i] = Queen(self.black_player.pieces[i].x, self.black_player.pieces[i].y, self.black_player.pieces[i].color, i)




class Player():
    def __init__(self, color, *input_pieces):
        if not(input_pieces):
            self.pieces = []
            self.color = color
            if color == 'White':
                self.king = King(4, 0, color, 4)

                self.pieces.append(Rook(0, 0, color, 0))
                self.pieces.append(Knight(1, 0, color, 1))
                self.pieces.append(Bishop(2, 0, color, 2))
                self.pieces.append(Queen(3, 0, color, 3))
                self.pieces.append(self.king)
                self.pieces.append(Bishop(5, 0, color, 5))
                self.pieces.append(Knight(6, 0, color, 6))
                self.pieces.append(Rook(7, 0, color, 7))
                self.pieces.append(Pawn(0, 1, color, 8))
                self.pieces.append(Pawn(1, 1, color, 9))
                self.pieces.append(Pawn(2, 1, color, 10))
                self.pieces.append(Pawn(3, 1, color, 11))
                self.pieces.append(Pawn(4, 1, color, 12))
                self.pieces.append(Pawn(5, 1, color, 13))
                self.pieces.append(Pawn(6, 1, color, 14))
                self.pieces.append(Pawn(7, 1, color, 15))

            elif color == 'Black':
                self.king = King(4, 7, color, 19)
                self.pieces.append(Rook(0, 7, color, 16))
                self.pieces.append(Knight(1, 7, color, 17))
                self.pieces.append(Bishop(2, 7, color, 18))
                self.pieces.append(self.king)
                self.pieces.append(Queen(3, 7, color, 20))
                self.pieces.append(Bishop(5, 7, color, 21))
                self.pieces.append(Knight(6, 7, color, 22))
                self.pieces.append(Rook(7, 7, color, 23))
                self.pieces.append(Pawn(0, 6, color, 24))
                self.pieces.append(Pawn(1, 6, color, 25))
                self.pieces.append(Pawn(2, 6, color, 26))
                self.pieces.append(Pawn(3, 6, color, 27))
                self.pieces.append(Pawn(4, 6, color, 28))
                self.pieces.append(Pawn(5, 6, color, 29))
                self.pieces.append(Pawn(6, 6, color, 30))
                self.pieces.append(Pawn(7, 6, color, 31))

            else:
                raise Exception('Invalid piece color for pawn, color is {0}'.format(color))
        else:
            self.pieces = input_pieces[0]
            self.color = color

    def print_pieces(self):
        print('len:', len(self.pieces))
        for i in self.pieces:
            print(write_position(i.get_position()), i.alive, type(i))

    def number_of_living_pieces(self):
        count = 0
        for i in self.pieces:
            if i.alive:
                count += 1
        return count

    def set_test_board(self):
        self.pieces = []
        if self.color == 'White':
            self.king = King(4, 0,  self.color, 4)
            self.pieces.append(Rook(7, 5,  self.color, 0))
            self.pieces.append(Rook(6, 6,  self.color, 0))
            self.pieces.append(Rook(5, 4,  self.color, 0))
            self.pieces.append(self.king)

        elif self.color == 'Black':
            self.king = King(0, 7, self.color, 19)
            self.pieces.append(self.king)

        else:
            raise Exception('Invalid piece color for pawn, color is {0}'.format(self.color))

    def get_players_possible_moves(self):
        moves = []
        for i in self.pieces:
            if i.alive:
                moves.extend(i.get_possible_piece_moves())
        return moves

    def is_color(self, color):
        if color == self.color:
            return True
        return False

class MovePortion():
    def __init__(self, begin_location, end_location, required_squares, piece_taken_location, move_name):
        self.begin_location = begin_location
        self.end_location = end_location
        self.required_squares = required_squares
        self.piece_taken_location = piece_taken_location
        self.move_name = move_name

    def get_move_tuple(self):
        return tuple([self.begin_location, self.end_location, self.piece_taken_location])

class Move():
    def __init__(self):
        self.move_portions = []

    def __init__(self, begin_location, end_location, other_squares_required, piece_taken_location, move_name):
        self.move_portions = []
        self.move_portions.append(MovePortion(begin_location, end_location, other_squares_required, piece_taken_location, move_name))

    def add_move(self, begin_location, end_location, other_squares_required, piece_taken_location, move_name):
        self.move_portions.append(MovePortion(begin_location, end_location, other_squares_required, piece_taken_location, move_name))

    def get_move_tuple(self):
        result = []
        for i in self.move_portions:
            result.append(i.get_move_tuple())
        return tuple(result)

class Piece():
    #pid is unique for all pieces
    #x,y are indexes 0 to 7 of rows and column, 0,0 is the white rook queenside, pawn in front of it is 0,1
    # (0,7), (1,7), (2,7)...
    # (0,6), (1,6), (2,6)...
    # (0,5), (1,5), (2,5)...

    def __init__(self, x, y, color, p_id):
        self.x = x
        self.y = y
        self.color = color
        self.alive = True
        self.name = None
        self.p_id = p_id

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

    def is_at_position(self, position):
        if position is not None and position == self.get_position():
            return True
        return False

    def is_at_position_and_alive(self, position):
        if position is not None and position == self.get_position_if_alive():
            return True
        return False

    def capture(self):
        self.alive = False

#TODO: add en passent
class Pawn(Piece):
    def __init__(self, x, y, color, p_id):
        super().__init__(x, y, color, p_id)
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
    def __init__(self, x, y, color, p_id):
        super().__init__(x, y, color, p_id)
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
    def __init__(self, x, y, color, p_id):
        super().__init__(x, y, color, p_id)
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
    def __init__(self, x, y, color, p_id):
        super().__init__(x, y, color, p_id)
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
    def __init__(self, x, y, color, p_id):
        super().__init__(x, y, color, p_id)
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
    def __init__(self, x, y, color, p_id):
        super().__init__(x, y, color, p_id)
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

def write_position(pos):
    if pos is None:
        return None
    else:
        a_ord = ord('a')
        result_str = chr(pos[0] + a_ord) + '' + str(pos[1] + 1)
        return result_str




