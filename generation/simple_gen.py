import tensorflow as tf


class SwaramQLearningAgent:

    def __init__(self, ep_len=32, n_layers=3, hidden_size=2048, batch_size=64, learning_rate=0.001,
                 epsilon=0.1, gamma=0.99):
        self.ep_len = ep_len
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.gamma = gamma
        self.sess = tf.Session()
        self.build_network()

    def build_qnet(self, inp):
        output = inp
        for _ in range(self.n_layers):
            output = tf.layers.dense(output, self.hidden_size)

        return output

    def build_network(self):
        init = tf.global_variables_initializer()
        self.input_placeholder = tf.placeholder(dtype=tf.int32, shape=[self.batch_size, self.ep_len])
        self.q_network = self.build_qnet(self.input_placeholder)
        self.sess.run(init)


if __name__ == '__main__':
    sqla = SwaramQLearningAgent()
