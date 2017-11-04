#TODO:draw up uml diagram to find inefficiencies
import copy

#TODO: Board 2 is replacement class that will allow more memoirization
#TODO: challenge, how to check for en passent or allow move history is such a system

class Board():
    def __init__(self):
        self.reset_players()
        self.position_dict = {}#stores if a position is in check

    def reset_players(self):
        self.players = {'White': Player('White'), 'Black': Player('Black')}

    def validate_moves(self, moves, player, opponent, block_checks):
        is_square_empty_or_opposite_color_dict = {}
        is_on_board_dict = {}
        is_move_type_valid_dict = {}
        is_square_empty_dict = {}

        valid_moves = []
        for m in moves:
            move_valid = True
            for i in m.moves:
                if not(is_square_empty_or_opposite_color_dict.setdefault((i['end_location'], i['piece_taken_location'], player.color, player, opponent),
                                                                         self.is_square_empty_or_opposite_color(
                                                                             i['end_location'],
                                                                             i['piece_taken_location'], player.color,
                                                                             player, opponent))):
                    move_valid = False
                    break
                if not (is_on_board_dict.setdefault((i['end_location'][0], i['end_location'][1]),
                                                    self.is_on_board(i['end_location'][0], i['end_location'][1])) ):
                    move_valid = False
                    break
                if not (is_move_type_valid_dict.setdefault((i['end_location'], player.color, i['move_name'], player, opponent),
                                                           self.is_move_type_valid(i['end_location'], player.color, i['move_name'], player, opponent))):
                    move_valid = False
                    break
                for j in i['other_squares_required']:
                    if not(is_on_board_dict.setdefault((j[0], j[1]),self.is_on_board(j[0], j[1]))) or not(is_square_empty_dict.setdefault((j[0], j[1], player, opponent), self.is_square_empty(j[0], j[1], player, opponent))):
                        move_valid = False
                        break
            if block_checks and self.is_in_check_after_move(player, opponent, m):
                continue
            if move_valid:
                valid_moves.append(m)
        return valid_moves

    def return_board(self, player1, player2):
        if player1.color == 'White':
            white_player = player1
            black_player = player2
        elif player1.color == 'Black':
            white_player = player2
            black_player = player1
        return_values = []
        for i in range(0, 16):
            piece = white_player.pieces[i]
            if piece.alive:
                return_values.append((piece.x, piece.y))
            else:
                return_values.append(None)
        for i in range(16, 32):
            piece = black_player.pieces[i]
            if piece.alive:
                return_values.append((piece.x, piece.y))
            else:
                return_values.append(None)
        return return_values

    def return_current_board(self):
        return self.return_board(self.players['White'], self.players['Black'])

    def print_move(self, move):
        temp = []
        for i in move.moves:
            temp.append([self.get_piece_by_id(i['piece_id']).color,
                        self.get_piece_by_id(i['piece_id']).name,
                         i['begin_location'], i['end_location']])
        return temp

    def get_piece_by_id(self, p_id):
        if self.players['White'].pieces.get(p_id, None) is not None:
            return self.players['White'].pieces.get(p_id, None)
        else:
            return self.players['Black'].pieces.get(p_id, None)

    def get_piece_by_location(self, loc):
        for _, p in self.players.items():
            for i in p.pieces.keys():
                if p.pieces[i].alive is True and p.pieces[i].x == loc[0] and p.pieces[i].y == loc[1]:
                    return p.pieces[i]

    def is_player_on_square(self,p_x,p_y, player):
        for i in player.pieces.keys():
            if player.pieces[i].alive is True and player.pieces[i].x == p_x and player.pieces[i].y == p_y:
                return True
        return False

    def get_other_color(self, color):
        if color == 'White':
            return 'Black'
        if color == 'Black':
            return 'White'

    def get_player(self, color):
        return

    def is_square_empty_or_opposite_color(self, end_loc, capture_loc, color, player1, player2):
        if player1.color == 'White':
            white_player = player1
            black_player = player2
        else:
            white_player = player2
            black_player = player1

        if end_loc != capture_loc and not(self.is_square_empty(end_loc[0], end_loc[1], player1, player2)):
            return False
        if color == 'White':
            return  self.is_square_empty(end_loc[0], end_loc[1], player1, player2) or self.is_player_on_square(end_loc[0], end_loc[1], black_player)
        if color == 'Black':
            return self.is_square_empty(end_loc[0], end_loc[1], player1, player2) or self.is_player_on_square(end_loc[0], end_loc[1], white_player)

    def is_piece_of_opposite_color_on_square(self, x, y, color, player1, player2):
        if player1.color == 'White':
            white_player = player1
            black_player = player2
        else:
            white_player = player2
            black_player = player1

        if color == 'White':
            return self.is_player_on_square(x,y, black_player)
        if color == 'Black':
            return self.is_player_on_square(x,y, white_player)

    def is_target_valid(self, move_x, move_y, target_x, target_y, player1, player2):
        if self.is_square_empty(move_x, move_y, player1, player2):
            return True
        if target_x == move_x and target_y == move_y and self.is_piece_of_opposite_color_on_square(move_x, move_y, player1.color, player1, player2):
            return True
        return False

    def is_square_empty(self, x, y, player1, player2):
        if player1.color == 'White':
            white_player = player1
            black_player = player2
        else:
            white_player = player2
            black_player = player1
        return not(self.is_player_on_square(x,y, white_player) or self.is_player_on_square(x,y, black_player))

    def is_on_board(self, x, y):
        if x >= 0 and x <= 7 and y >= 0 and y <= 7:
            return True
        return False

    def is_move_type_valid(self, end_loc, color, move_type, p1, p2):
        if move_type == 'Pawn capture' and not(self.is_piece_of_opposite_color_on_square(end_loc[0], end_loc[1], color, p1, p2)):
            return False
        return True

    def get_valid_moves(self, player, opponent, block_checks):
        #return self.position_valid_move_dict.setdefault((tuple(self.return_board(player, opponent)), player.color, block_checks), self.validate_moves(player.get_players_possible_moves(), player, opponent, block_checks))
        return self.validate_moves(player.get_players_possible_moves(), player, opponent, block_checks)

    def is_in_check(self, player, opponent):
        moves = self.get_valid_moves(opponent, player, True)
        king_position = (player.pieces[player.king_id].x, player.pieces[player.king_id].y)
        for m in moves:
            for i in m.moves:
                if i['piece_taken_location'] ==  king_position:
                    return True
        return False

    def execute_move(self, player, opponent, move):
        for m in move.moves:
            for _, value in opponent.pieces.items():
                if m['piece_taken_location'] is not None and value.x == m['piece_taken_location'][0] and value.y == m['piece_taken_location'][1]:
                    value.alive = False
            player.pieces[m['piece_id']].x =  m['end_location'][0]
            player.pieces[m['piece_id']].y = m['end_location'][1]
        for p_id, p in player.pieces.items():
            if m['piece_id'] == p_id:
                p.move_history.append(move)
            else:
                p.move_history.append(None)
        for p_id, p in opponent.pieces.items():
            p.move_history.append(None)
        self.update_pawns_at_board_end()

    def capture_piece(self, player, loc):
        for _, value in player.pieces.items():
            if value.x == loc[0] and value.y == loc[1]:
                value.alive = False

    def get_board_copy_after_move(self,  player, opponent, move):
        temp_player = copy.deepcopy(player)
        temp_opponent = copy.deepcopy(opponent)
        for m in move.moves:
            temp_player.pieces[m['piece_id']].x = m['end_location'][0]
            temp_player.pieces[m['piece_id']].y = m['end_location'][1]
            if m['piece_taken_location'] is not None:
                self.capture_piece(temp_opponent, m['piece_taken_location'])
        return temp_player, temp_opponent

    #checks if the post move version has already been calculated, if not it calculates it
    def is_in_check_after_move(self, player, opponent, move):
        temp_player, temp_opponent = self.get_board_copy_after_move(player, opponent, move)
        '''try:
            saved_board = tuple(self.return_board(temp_player, temp_opponent))
            return self.position_dict.setdefault((saved_board, player.color, move.moves[0]['begin_location'], move.moves[0]['end_location'], len(move.moves)),
                                          self.is_in_check_aftr_move_checker(temp_player, temp_opponent, player))
        except:'''
        return self.is_in_check_after_move_checker(temp_player, temp_opponent, player)

    #gets called if combination not in dict
    def is_in_check_after_move_checker(self, temp_player, temp_opponent, player):
        opponent_moves = self.get_valid_moves(temp_opponent, temp_player, False)
        king_position = (temp_player.pieces[player.king_id].x, temp_player.pieces[player.king_id].y)
        for m in opponent_moves:
            for i in m.moves:
                if i['piece_taken_location'] is not None and i['piece_taken_location'][0] ==  king_position[0] and i['piece_taken_location'][1] ==  king_position[1]:
                    return True
        return False

    def is_in_checkmate_after_move(self, player, opponent, move):
        temp_player, temp_opponent = self.get_board_copy_after_move(player, opponent, move)
        return self.is_in_checkmate(temp_player, temp_opponent)

    def is_in_checkmate(self, player, opponent):
        if self.is_in_check(player, opponent) and len(self.get_valid_moves(player,opponent, True))==0:
            return True
        return False

    def is_draw(self, player, opponent):
        if not(self.is_in_check(player, opponent)) and len(self.get_valid_moves(player,opponent, True))==0:
            return True
        return False

    def get_move_that_would_checkmate(self, moves, player, opponent):
        #moves = self.get_valid_moves(player, opponent, True)
        for i in moves:
            #print(i.__dict__)
            if self.is_in_checkmate_after_move(player, opponent, i):
                return i
        return None

    #casteling, en passent
    def get_special_moves(self, player):
        if player.color == 'White':
            pass

    def update_pawns_at_board_end(self):

        for i in range(0, 32):

            piece = self.get_piece_by_id(i)

            if piece.name == 'Pawn' and piece.color == 'White' and piece.y == 7:
                print('updating pawn')
                print(piece.__dict__)
                pawns_move_history = copy.deepcopy(piece.move_history)
                self.players['White'].pieces[i] = Queen(piece.x, piece.y, piece.color)
                self.players['White'].pieces[i].move_history = pawns_move_history
                print(self.players['White'].pieces[i].__dict__)
            elif piece.name == 'Pawn' and piece.color == 'Black' and piece.y == 0:
                print('updating pawn')
                print(piece.__dict__)
                pawns_move_history = copy.deepcopy(piece.move_history)
                self.players['Black'].pieces[i] = Queen(piece.x, piece.y, piece.color)
                self.players['Black'].pieces[i].move_history = pawns_move_history
                print(self.players['White'].pieces[i].__dict__)

class Player():
    def __init__(self, color, *input_pieces):
        if not(input_pieces):
            self.pieces = {}
            self.color = color
            if color == 'White':
                self.king_id = 4

                self.pieces[0] = Rook(0, 0, color)
                self.pieces[1] = Knight(1, 0, color)
                self.pieces[2] = Bishop(2, 0, color)
                self.pieces[3] = Queen(3, 0, color)
                self.pieces[4] = King(4, 0, color)
                self.pieces[5] = Bishop(5, 0, color)
                self.pieces[6] = Knight(6, 0, color)
                self.pieces[7] = Rook(7, 0, color)
                self.pieces[8] = Pawn(0, 1, color)
                self.pieces[9] = Pawn(1, 1, color)
                self.pieces[10] = Pawn(2, 1, color)
                self.pieces[11] = Pawn(3, 1, color)
                self.pieces[12] = Pawn(4, 1, color)
                self.pieces[13] = Pawn(5, 1, color)
                self.pieces[14] = Pawn(6, 1, color)
                self.pieces[15] = Pawn(7, 1, color)

            elif color == 'Black':
                self.king_id = 19
                self.pieces[16] = Rook(0, 7, color)
                self.pieces[17] = Knight(1, 7, color)
                self.pieces[18] = Bishop(2, 7, color)
                self.pieces[19] = King(3, 7, color)
                self.pieces[20] = Queen(4, 7, color)
                self.pieces[21] = Bishop(5, 7, color)
                self.pieces[22] = Knight(6, 7, color)
                self.pieces[23] = Rook(7, 7, color)
                self.pieces[24] = Pawn(0, 6, color)
                self.pieces[25] = Pawn(1, 6, color)
                self.pieces[26] = Pawn(2, 6, color)
                self.pieces[27] = Pawn(3, 6, color)
                self.pieces[28] = Pawn(4, 6, color)
                self.pieces[29] = Pawn(5, 6, color)
                self.pieces[30] = Pawn(6, 6, color)
                self.pieces[31] = Pawn(7, 6, color)

            else:
                raise Exception('Invalid piece color for pawn, color is {0}'.format(color))
        else:
            self.pieces = input_pieces[0]
            self.color = color

    def get_players_possible_moves(self):
        moves = []
        for i in self.pieces.keys():
            if self.pieces[i].alive:
                moves.extend(self.pieces[i].get_possible_piece_moves(i))
        return moves

#read list of move
#required to take input as list for special moves
#move name required to allow board to determine if en passsant is possible
class Move():
    def __init__(self):
        self.moves = []

    def __init__(self, begin_location, end_location, other_squares_required, piece_taken_location, piece_id, move_name):
        self.moves = []
        self.moves.append({'begin_location':begin_location,
                           'end_location':end_location,
                           'other_squares_required':other_squares_required,
                           'piece_taken_location':piece_taken_location,
                           'piece_id':piece_id,
                           'move_name':move_name})

    def add_move(self, begin_location, end_location, other_squares_required, piece_taken_location, piece_id, move_name):
        self.moves.append({'begin_location':begin_location,
                           'end_location':end_location,
                           'other_squares_required':other_squares_required,
                           'piece_taken_location':piece_taken_location,
                           'piece_id':piece_id,
                           'move_name':move_name})
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
        self.move_history = []
        self.alive = True
        self.name = None

    def get_possible_piece_moves(self):
        moves = []
        if not(self.alive):
            return moves

#TODO: add en passent
class Pawn(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Pawn'

    def get_possible_piece_moves(self, p_id):
        super().get_possible_piece_moves()
        moves = []

        if self.color == 'White':
            if self.y == 1:
                moves.append(Move((self.x, self.y), (self.x, self.y+2), [(self.x, self.y+ 1)], None, p_id, 'Pawn double move'))
            moves.append(Move((self.x, self.y), (self.x, self.y + 1), [], None, p_id, 'Pawn move'))
            moves.append(Move((self.x, self.y), (self.x + 1, self.y + 1), [], (self.x + 1, self.y + 1), p_id, 'Pawn capture'))
            moves.append(Move((self.x, self.y), (self.x - 1, self.y + 1), [], (self.x - 1, self.y + 1), p_id, 'Pawn capture'))

        elif self.color == 'Black':
            if self.y == 6:
                moves.append(Move((self.x, self.y), (self.x, self.y - 2), [(self.x, self.y - 1)], None, p_id, 'Pawn double move'))
            moves.append(Move((self.x, self.y), (self.x, self.y - 1), [], None, p_id, 'Pawn move'))
            moves.append(Move((self.x, self.y), (self.x + 1, self.y - 1), [], (self.x + 1, self.y - 1), p_id, 'Pawn capture'))
            moves.append(Move((self.x, self.y), (self.x - 1, self.y - 1), [], (self.x - 1, self.y - 1), p_id, 'Pawn capture'))
        else:
            raise Exception('Invalid piece color for pawn, color is {0}, piece_id:{1}')
        return moves

class Rook(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Rook'

    def get_possible_piece_moves(self, p_id):
        super().get_possible_piece_moves()
        moves = []

        for i in range(1,8):
            moves.append(Move((self.x, self.y), (self.x, self.y + i),
                              [(self.x, self.y + j) for j in range(1, i)],
                              (self.x, self.y + i), p_id, 'Rook move'))
            moves.append(Move((self.x, self.y), (self.x, self.y - i),
                              [(self.x, self.y - j) for j in range(1, i)],
                              (self.x, self.y - i), p_id, 'Rook move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y),
                              [(self.x + j, self.y) for j in range(1, i)],
                              (self.x + i, self.y), p_id, 'Rook move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y),
                              [(self.x - j, self.y) for j in range(1, i)],
                              (self.x - i, self.y), p_id, 'Rook move'))
        return moves

class Bishop(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Bishop'

    def get_possible_piece_moves(self, p_id):
        super().get_possible_piece_moves()
        moves = []

        for i in range(1,8):
            moves.append(Move((self.x, self.y), (self.x + i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x + i, self.y + i), p_id, 'Bishop move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x + i, self.y - i), p_id, 'Bishop move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x - i, self.y + i), p_id, 'Bishop move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x - i, self.y - i), p_id, 'Bishop move'))
        return moves

class Knight(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Knight'

    def get_possible_piece_moves(self, p_id):
        super().get_possible_piece_moves()
        moves = []
        moves.append(Move((self.x, self.y), (self.x + 1, self.y + 2), [], (self.x + 1, self.y + 2), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x + 1, self.y - 2), [], (self.x + 1, self.y - 2), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 1, self.y + 2), [], (self.x - 1, self.y + 2), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 1, self.y - 2), [], (self.x - 1, self.y - 2), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x + 2, self.y + 1), [], (self.x + 2, self.y + 1), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x + 2, self.y - 1), [], (self.x + 2, self.y - 1), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 2, self.y + 1), [], (self.x - 2, self.y + 1), p_id, 'Knight move'))
        moves.append(Move((self.x, self.y), (self.x - 2, self.y - 1), [], (self.x - 2, self.y - 1), p_id, 'Knight move'))
        return moves

class King(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'King'

    def get_possible_piece_moves(self, p_id):
        super().get_possible_piece_moves()
        moves = []
        moves.append(Move((self.x, self.y), (self.x, self.y + 1),[], (self.x, self.y + 1), p_id, 'King move'))
        moves.append(Move((self.x, self.y),(self.x, self.y - 1),[], (self.x, self.y - 1), p_id,'King move'))
        moves.append(Move((self.x, self.y),(self.x - 1, self.y + 1),[], (self.x - 1, self.y + 1), p_id,'King move'))
        moves.append(Move((self.x, self.y),(self.x - 1, self.y),[], (self.x - 1, self.y), p_id,'King move'))
        moves.append(Move((self.x, self.y),(self.x - 1, self.y - 1),[], (self.x - 1, self.y - 1), p_id,'King move'))
        moves.append(Move((self.x, self.y),(self.x + 1, self.y + 1),[], (self.x + 1, self.y + 1), p_id,'King move'))
        moves.append(Move((self.x, self.y),(self.x + 1, self.y ),[], (self.x + 1, self.y ), p_id,'King move'))
        moves.append(Move((self.x, self.y),(self.x + 1, self.y - 1),[], (self.x + 1, self.y - 1), p_id,'King move'))
        return moves

class Queen(Piece):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.name = 'Queen'

    def get_possible_piece_moves(self, p_id):
        super().get_possible_piece_moves()
        moves = []

        for i in range(1,8):
            moves.append(Move((self.x, self.y), (self.x + i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x + i, self.y + i), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x + i, self.y - i), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y + i),
                              [(self.x + j, self.y + j) for j in range(1, i)],
                              (self.x - i, self.y + i), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y - i),
                              [(self.x - j, self.y - j) for j in range(1, i)],
                              (self.x - i, self.y - i), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x, self.y + i),
                              [(self.x, self.y + j) for j in range(1, i)],
                              (self.x, self.y + i), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x, self.y - i),
                              [(self.x, self.y - j) for j in range(1, i)],
                              (self.x, self.y - i), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x + i, self.y),
                              [(self.x + j, self.y) for j in range(1, i)],
                              (self.x + i, self.y), p_id, 'Queen move'))
            moves.append(Move((self.x, self.y), (self.x - i, self.y),
                              [(self.x - j, self.y) for j in range(1, i)],
                              (self.x - i, self.y), p_id, 'Queen move'))
        return moves


