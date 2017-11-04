import sqlite3
import random
import game_engine
import time
import traceback

class Player():
    def __init__(self, name):
        self.name = name

    def pick_move(self, moves, b, opponent):
        pass

    def assign_board_side(self, board_player):
        self.board_side = board_player

class PlayerRandom(Player):
    def __init__(self, name):
        super().__init__(name)

    def pick_move(self, moves, b, opponent):
        super().pick_move(moves, b, opponent)
        return random.choice(moves)

class PlayerOpportunisticRandom(Player):
    def __init__(self, name):
        super().__init__(name)
        self.max_moves_to_check = 5 #for speed

    def pick_move(self, moves, b, opponent):
        super().pick_move(moves, b, opponent)
        result = b.get_move_that_would_checkmate(moves, self.board_side, opponent)
        if result is None:
            return random.choice(moves)
        else:
            return result

class Game():
    def __init__(self, player1, player2, board):
        self.b = board
        self.player1 = player1
        self.player2 = player2
        self.player1.assign_board_side(self.b.players['White'])
        self.player2.assign_board_side(self.b.players['Black'])



        self.set_up_db()

    def run_game(self, max_moves):
        self.w_win = False
        self.b_win = False
        self.draw = False
        self.b.reset_players()
        print('White:', self.player1.name)
        print('Black:', self.player2.name)
        game_id = self.get_game_id()

        positions = []
        start = time.time()
        move = 1
        print('game:', game_id)
        while move < max_moves:
            print()
            print('move:', move, ',time:', time.time() - start,
                  ',White pieces:',
                  sum([1 if x.alive else 0 for _, x in self.player1.board_side.pieces.items()]),
                  ',Black pieces',
                  sum([1 if x.alive else 0 for _, x in self.player2.board_side.pieces.items()]))
            #print('White number of pieces', sum([1 if x.alive else 0 for _, x in self.player1.board_side.pieces.items()]))
            #print('Black number of pieces', sum([1 if x.alive else 0 for _, x in self.player2.board_side.pieces.items()]))

            white_move = self.player1.pick_move(self.b.get_valid_moves(self.player1.board_side, self.player2.board_side, True), self.b, self.player2.board_side)
            #print('White:')
            for i in self.b.print_move(white_move):
                print(i)
            self.b.execute_move(self.player1.board_side, self.player2.board_side, white_move)

            positions.append([move, 'White', self.b.return_current_board()])

            if self.is_game_over():
                break

            black_move = self.player2.pick_move(self.b.get_valid_moves(self.player2.board_side, self.player1.board_side, True), self.b, self.player2.board_side)
            #print('Blacks move:')
            for i in self.b.print_move(black_move):
                print(i)
            self.b.execute_move(self.player2.board_side, self.player1.board_side, black_move)
            positions.append([move, 'Black', self.b.return_current_board()])

            if self.is_game_over():
                break
            move += 1
        try:
            if self.w_win:
                self.write_board_to_db(positions, self.w_win, self.b_win, game_id)
            elif self.b_win:
                self.write_board_to_db(positions, self.w_win, self.b_win, game_id)
        except:
            traceback.print_exc()

    def is_game_over(self):
        if self.b.is_draw(self.b.players['White'], self.b.players['Black']):
            print('draw')
            self.draw = True
            return True
        if self.b.is_in_checkmate(self.b.players['White'], self.b.players['Black']):
            print('Black wins')
            self.b_win = True
            return True
        if self.b.is_in_checkmate(self.b.players['Black'], self.b.players['White']):
            print('White wins')
            self.w_win = True
            return True
        return False

    def get_game_id(self):
        try:
            conn = sqlite3.connect('chess.db')
            game_id = max(i[0] for i in list(conn.execute('select game_id from games').fetchall())) + 1
            return game_id
        except:
            traceback.print_exc()
            return 0

    def write_board_to_db(self, positions, w_win, b_win, game_id):
        conn = sqlite3.connect('chess.db')

        #p, [move, turn, position]
        for  p in positions:
            print([game_id, p[0], p[1]] + [i[0]*8 + i[1] for i in p[2]])
            conn.execute('''insert into positions values (?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', [game_id, p[0], p[1]] + [i[0]*8 + i[1] for i in p[2]])
        try:
            if w_win:
                conn.execute('insert into games values(?,?)', [game_id, 'White'])
            else:
                conn.execute('insert into games values(?,?)', [game_id, 'Black'])
        except:
            traceback.print_exc()
        conn.commit()
        conn.close()

    def set_up_db(self):
        conn = sqlite3.connect('chess.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS games (
        game_id int  PRIMARY KEY,
        winner text)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS positions (
        game_id int, move int, turn text,
        p0 int, p1 int, p2 int, p3 int, p4 int, p5 int, p6 int, p7 int, p8 int, p9 int, p10 int, p11 int, p12 int, p13 int, p14 int, p15 int,
        p16 int, p17 int, p18 int, p19 int, p20 int, p21 int, p22 int, p23 int, p24 int, p25 int, p26 int, p27 int, p28 int, p29 int, p30 int, p31 int
        )''')
        conn.commit()
        conn.close()

b = game_engine.Board()
max_moves = 100
while True:
    if max_moves < 100:
        max_moves += 1
    try:
        p1 = PlayerRandom('W')
        p2 = PlayerRandom('B')
        g = Game(p1, p2, b)
        g.run_game(max_moves)
    except:
        traceback.print_exc()
