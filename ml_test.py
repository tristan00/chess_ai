import tensorflow as tf
import sqlite3
import random
import numpy as np
import time

max_moves_to_record_in_input = 20

def train_neural_network(self, word_list_size, nodes_per_layer, refresh):
    start_time = time.time()
    print('Reading data:', time.time() -start_time)
    if self.inputs is None or refresh:
        self.inputs = self.get_data(word_list_size)
    train_x, train_y, test_x, test_y = self.create_feature_sets_and_labels(.1, self.inputs)

    #data = tf.placeholder('float')
    print('Building network:', time.time() -start_time)
    self.x = tf.placeholder('float', [None, len(train_x[0])])
    self.y = tf.placeholder('float', [None, 2])
    self.prediction = self.neural_network_model(train_x, train_y, test_x, test_y, nodes_per_layer)
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.prediction, labels=self.y))
    print('Building optimizer:', time.time() -start_time)
    optimizer = tf.train.AdamOptimizer().minimize(cost)
    batch_size = 10
    hm_epochs = 10
    print('Running session:', time.time() -start_time)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for epoch in range(hm_epochs):
            epoch_loss = 0
            i=0
            while i < len(train_x):
                start = i
                end = i + batch_size
                batch_x = np.array(train_x[start:end])
                batch_y = np.array(train_y[start:end])
                _, c = sess.run([optimizer, cost], feed_dict= {self.x:batch_x, self.y:batch_y})
                epoch_loss += c
                i += batch_size
            print("Epoch", epoch, 'completed out of', hm_epochs, 'loss:', epoch_loss)
        correct = tf.equal(tf.argmax(self.prediction, 1), tf.argmax(self.y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        accuracy_float = accuracy.eval(feed_dict = {self.x:test_x, self.y:test_y})
        print('Finished learning, time taken:', time.time() - start_time)



        for i in zip(test_x, test_y):
            print()
            batch_x = i[0]
            print('Batch:', batch_x)
            predictions = sess.run(self.prediction, feed_dict = {self.x:[i[0]]})
            print('Prediction:', predictions, 'Result:', i[1])



# crestes 10 layer neural network
def neural_network_model(self, train_x, train_y, test_x, test_y, nodes_per_layer):
    n_classes = 2

    hidden_1_layer = {'weights': tf.Variable(tf.random_normal([len(train_x[0]), nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_2_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_3_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_4_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_5_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_6_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_7_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_8_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_9_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    hidden_10_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, nodes_per_layer])),
                      'biases': tf.Variable(tf.random_normal([nodes_per_layer]))}
    output_layer = {'weights': tf.Variable(tf.random_normal([nodes_per_layer, n_classes])),
                        'biases': tf.Variable(tf.random_normal([n_classes]))}

    l1 = tf.add(tf.matmul(self.x, hidden_1_layer['weights']), hidden_1_layer['biases'])
    l1 = tf.nn.relu(l1)
    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.nn.relu(l2)
    l3 = tf.add(tf.matmul(l2, hidden_3_layer['weights']), hidden_3_layer['biases'])
    l3 = tf.nn.relu(l3)
    l4 = tf.add(tf.matmul(l3, hidden_4_layer['weights']), hidden_4_layer['biases'])
    l4 = tf.nn.relu(l4)
    l5 = tf.add(tf.matmul(l4, hidden_5_layer['weights']), hidden_5_layer['biases'])
    l5 = tf.nn.relu(l5)
    l6 = tf.add(tf.matmul(l5, hidden_6_layer['weights']), hidden_6_layer['biases'])
    l6 = tf.nn.relu(l6)
    l7 = tf.add(tf.matmul(l1, hidden_7_layer['weights']), hidden_7_layer['biases'])
    l7 = tf.nn.relu(l7)
    l8 = tf.add(tf.matmul(l2, hidden_8_layer['weights']), hidden_8_layer['biases'])
    l8 = tf.nn.relu(l8)
    l9 = tf.add(tf.matmul(l3, hidden_9_layer['weights']), hidden_9_layer['biases'])
    l9 = tf.nn.relu(l9)
    l10 = tf.add(tf.matmul(l4, hidden_10_layer['weights']), hidden_10_layer['biases'])
    l10 = tf.nn.relu(l10)
    output = tf.matmul(l5, output_layer['weights']) +   output_layer['biases']
    return output

#reads inputs as an array representing the location of piece ids, moves, turn to play
def read_inputs():
    conn = sqlite3.connect('chess.db')
    results = list(conn.execute('select positions.*, games.* from positions join games on games.game_id = positions.game_id').fetchall())

    inputs = []
    for i in results:
        inputs.append([turn_position_db_entry_into_input(i), turn_result_into_inputs(i)])


def turn_position_db_entry_into_input(db_input):
    temp = []
    moves = db_input[1]
    move_input = [0 for i in range(max_moves_to_record_in_input + 1)]
    if moves < max_moves_to_record_in_input:
        move_input[moves] = 1
    else:
        move_input[-1] = 1

    temp.extend(move_input)

    turn = db_input[1]
    if turn == 'White':
        turn_input = [1, 0]
    elif turn == 'Black':
        turn_input = [0, 1]

    temp.extend(turn_input)

    for i in db_input[3:]:
        value_tuple = (i//8, i%8)
        x_input = [0 for i in range(8)]
        y_input = [0 for i in range(8)]
        x_input[value_tuple[0]] = 1
        y_input[value_tuple[1]] = 1
        temp.extend(x_input)
        temp.extend(y_input)
    return temp

def turn_result_into_inputs(db_input):
    if db_input[-1] == 'White':
        return [1, 0]
    elif db_input[-1] == 'Black':
        return [0, 1]


def create_feature_sets_and_labels(self, test_size,  inputs):
    random.shuffle(inputs)
    features = np.array(inputs)

    testing_size = int(test_size*len(features))
    train_x = list(features[:,0][:-testing_size])
    train_y = list(features[:,1][:-testing_size])
    test_x = list(features[:,0][testing_size:])
    test_y = list(features[:,1][testing_size:])

    return train_x, train_y, test_x, test_y
