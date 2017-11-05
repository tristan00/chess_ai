import sqlite3
import random
import game_engine2
import ml_model
import time
import tensorflow as tf
import sqlite3
import numpy as np
import traceback

ml_model_data = None

class Player():
    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.board_player = None

    def close_variables(self):
        pass

    def pick_move(self, move_num):
        pass

    def get_board_player(self):
        self.board_player = self.board.get_player_by_color(self.color)

class PlayerRandom(Player):
    def __init__(self, board, color):
        super().__init__(board, color)

    def pick_move(self, move_num):
        super().pick_move(move_num)
        results = self.board.analyze_round_and_get_valid_moves(self.color)
        if len(results[1]) > 0 :
            move = random.choice(results[1])
        else:
            move = []
        moves = [results[0], move]
        return moves

class PlayerOpportunisticRandom(Player):
    def __init__(self, board, color):
        super().__init__(board, color)

    def pick_move(self, move_num):
        super().pick_move(move_num)
        results = self.board.analyze_round_and_get_checkmate_moves(self.color)
        if len(results[1]) > 0 :
            move = random.choice(results[1])
        else:
            move = []
        moves = [results[0], move]
        return moves

class PlayerNN(Player):
    def __init__(self, board, color):
        super().__init__(board, color)

    def pick_move(self, move_num):
        super().pick_move(move_num)
        results = self.board.analyze_round_and_get_nn(self.color)
        code = results[0]
        data = results[1]

        for i in data:
            temp = [move_num, self.color]
            temp.extend(i[1])
            i[2] = ml_model.turn_input_into_features(temp)

        for i in data:
            batch_x = i[2]
            predictions = ml_model_data.run_input(batch_x)
            #print('prediction:', predictions)
            if self.color == game_engine2.white_color_str:
                i[3] = predictions[0][0]
            elif self.color == game_engine2.black_color_str:
                i[3] = predictions[0][1]

        picked_move = sorted(data, key=lambda x: x[3], reverse = True)[0][0]
        moves = [code, picked_move]
        return moves

    def close_variables(self):
        super().close_variables()

class Game():
    def __init__(self, white_player, black_player, board):
        self.b = board
        self.white_player = white_player
        self.black_player = black_player
        self.set_up_db()

    def run_game(self):
        self.w_win = False
        self.b_win = False
        self.draw = False
        self.b.reset_players()
        self.b.reset_dicts()

        self.white_player.get_board_player()
        self.black_player.get_board_player()

        game_id = self.get_game_id()

        positions = []
        start = time.time()
        move = 1
        print('game:', game_id)
        while True:
            print()
            print('move:', move, ',time:', time.time() - start,
                  ',White pieces:',
                  sum([1 if x.alive else 0 for x in self.white_player.board_player.pieces]),
                  ',Black pieces',
                  sum([1 if x.alive else 0 for x in self.black_player.board_player.pieces]))
            move_result = self.white_player.pick_move(move)
            if self.is_game_over(move_result, self.white_player.color):
                break

            print_move(move_result, game_engine2.white_color_str)
            #self.white_player.board_player.print_pieces()

            self.b.execute_move(self.white_player.board_player, self.black_player.board_player, self.white_player.color, move_result[1])
            positions.append([move, 'White', self.b.get_board_tuple(self.white_player.board_player ,self.black_player.board_player)])

            move_result = self.black_player.pick_move(move)
            if self.is_game_over(move_result, self.black_player.color):
                break
            print_move(move_result, game_engine2.black_color_str)
            #self.black_player.board_player.print_pieces()
            self.b.execute_move(self.white_player.board_player, self.black_player.board_player, self.black_player.color, move_result[1])
            positions.append([move, 'Black', self.b.get_board_tuple(self.white_player.board_player ,self.black_player.board_player)])
            move += 1
        try:
            if self.w_win:
                self.write_board_to_db(positions, self.w_win, self.b_win, game_id)
                return 1
            elif self.b_win:
                self.write_board_to_db(positions, self.w_win, self.b_win, game_id)
                return 2
            else:
                return 3
        except:
            traceback.print_exc()
            return 4

    def is_game_over(self, result, color):
        if result[0] == game_engine2.checkmate_code and color == game_engine2.white_color_str:
            print('Black wins')
            self.b_win = True
            return True
        if result[0] == game_engine2.checkmate_code and color == game_engine2.black_color_str:
            print('White wins')
            self.w_win = True
            return True
        if result[0] == game_engine2.draw_code:
            print('draw')
            self.draw = True
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
            print(p)
            temp_data = []
            p2_record = []
            for i in p[2]:
                if i is None:
                    p2_record.append(None)
                else:
                    p2_record.append(i[0]*8 + i[1])


            temp_data.extend([game_id, p[0], p[1]])
            temp_data.extend(p2_record)
            conn.execute('''insert into positions values (?,?,?,
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',   [i for i in temp_data])

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

def print_move(move, color):
    print(color + ':')
    for i in move[1]:
        print(game_engine2.write_position(i[0]), game_engine2.write_position(i[1]), game_engine2.write_position(i[2]))



def main():
    global ml_model_data
    seed = random.random()
    b = game_engine2.Board()
    games_to_play = 100
    player_results = {}
    ml_model_data = ml_model.Model(5)

    for i in range(games_to_play):
        print('results:')
        for i, j in player_results.items():
            print(i, j)
        print()
        try:
            if seed < .25:
                p1 = PlayerRandom(b, game_engine2.white_color_str)
                p2 = PlayerNN(b, game_engine2.black_color_str)
            elif seed < .5:
                p1 = PlayerNN(b, game_engine2.white_color_str)
                p2 = PlayerRandom(b, game_engine2.black_color_str)
            elif seed < .75:
                p1 = PlayerRandom(b, game_engine2.white_color_str)
                p2 = PlayerRandom(b, game_engine2.black_color_str)
            else:
                p1 = PlayerNN(b, game_engine2.white_color_str)
                p2 = PlayerNN(b, game_engine2.black_color_str)

            g = Game(p1, p2, b)
            result = g.run_game()
            player_results[result] = player_results.get(result, 0) + 1
            p1.close_variables()
            p2.close_variables()
        except:
            time.sleep(10)
            traceback.print_exc()

    ml_model_data.close_session()
    del ml_model_data

for i in range(100):
    main()
