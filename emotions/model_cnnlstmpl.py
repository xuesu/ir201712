import json
import tensorflow as tf


class LSTMModel(object):
    def __init__(self, mes, graph):
        self.mes = mes
        self.graph = graph
        self.step_num = mes.config['DG_STEP_NUM']
        self.sentence_sz = self.mes.config['DG_SENTENCE_SZ']
        self.label_num = self.mes.config['LABEL_NUM']
        self.c_fids = mes.config['PRE_C_FIDS']
        self.emb_fids = mes.config['PRE_EMB_FIDS']
        for fid in self.emb_fids:
            assert(fid in mes.config['W2V_TRAIN_FIDS'])
        self.one_hot_fids = mes.config['PRE_ONE_HOT_FIDS']
        self.one_hot_depths = mes.config['PRE_ONE_HOT_DEPTHS']
        self.convs_level_nums = mes.config['PRE_CONVS_LEVEL_NUMS']
        self.convs_kernel_nums = mes.config['PRE_CONVS_KERNEL_NUMS']
        self.convs_strides = mes.config['PRE_CONVS_STRIDES']
        self.convs_filter_nums = mes.config['PRE_CONVS_FILTER_NUMS']
        self.pools_sizes = mes.config['PRE_POOLS_SIZES']
        self.pools_strides = mes.config['PRE_POOLS_STRIDES']
        self.linear1_sz = mes.config['PRE_LINEAR1_SZ']
        self.lstm_sz = mes.config['PRE_LSTM_SZ']
        self.linear2_sz = mes.config['PRE_LINEAR2_SZ']
        self.learning_rate = mes.config['PRE_E_LEARNING_RATE']

        assert(len(self.one_hot_fids) == len(self.one_hot_depths))
        self.fids = set(self.c_fids + self.emb_fids + self.one_hot_fids)
        for fid in self.fids:
            assert(fid in mes.config['DG_FIDS'])
        with self.graph.as_default():
            # input_value
            with tf.name_scope("Input") as scope:
                self.train_dataset = {}
                for fid in self.fids:
                    if fid in self.c_fids:
                        self.train_dataset[fid] = tf.placeholder(tf.float32,
                                                                 shape=[self.step_num, None, self.sentence_sz],
                                                                 name="DataBatch_{}".format(fid))
                    else:
                        self.train_dataset[fid] = tf.placeholder(tf.int32,
                                                                 shape=[self.step_num, None, self.sentence_sz],
                                                                 name="DataBatch_{}".format(fid))
                self.train_labels = tf.placeholder(tf.int32, shape=[None, self.label_num], name="Label")
                # variable
                with tf.name_scope("One_hot") as sub_scope:
                    self.one_hots = []
                    for fid, depth in zip(self.one_hot_fids, self.one_hot_depths):
                        self.one_hots.append(tf.to_float(tf.one_hot(self.train_dataset[fid], depth=depth, axis=-1,
                                                                    dtype=tf.int32, name="One_hot_{}".format(fid))))
                with tf.name_scope("Embedding"):
                    self.embeddings = {}
                    self.embeds = []
                    for fid in self.emb_fids:
                        with open(mes.get_feature_emb_path(fid)) as fin:
                            init_embedding = json.load(fin)
                        self.embeddings[fid] = tf.Variable(init_embedding, name="Embedding_{}".format(fid))
                        # model
                        self.embeds.append(tf.nn.embedding_lookup(self.embeddings[fid], self.train_dataset[fid],
                                                                  name="Embed_{}".format(fid)))
                with tf.name_scope("Continuous_Feature") as sub_scope:
                    self.cfeatures = []
                    for fid in self.c_fids:
                        self.cfeatures.append(tf.expand_dims(self.train_dataset[fid], -1,
                                                             "Continuous_Feature_{}".format(fid)))
                with tf.name_scope("Concat") as sub_scope:
                    self.concat_input = tf.concat(self.embeds + self.one_hots + self.cfeatures, -1)
                    concat_input_dim = int(self.concat_input.shape[-1])
                    print concat_input_dim
                    self.concat_reshape = tf.reshape(self.concat_input, shape=[-1, self.sentence_sz, concat_input_dim])
            with tf.name_scope("Convnet") as scope:
                self.convss = []
                self.poolss = []
                concat_inputs = [self.concat_reshape]
                for i in range(self.convs_level_nums):
                    convs = []
                    pools = []
                    for conv_knum, conv_stride, pool_size, pool_stride in zip(self.convs_kernel_nums[i],
                                                                              self.convs_strides[i],
                                                                              self.pools_sizes[i],
                                                                              self.pools_strides[i]):
                        for input in concat_inputs:
                            conv = tf.layers.conv1d(input, self.convs_filter_nums[i], conv_knum, conv_stride,
                                                    use_bias=True, activation=tf.nn.relu, padding="same")
                            if pool_size == -1 or pool_stride == -1:
                                pool_size = pool_stride = int(conv.shape[-2])
                            pool = tf.layers.max_pooling1d(conv, pool_size, pool_stride, padding="same")
                            convs.append(conv)
                            pools.append(pool)
                    self.convss.append(convs)
                    self.poolss.append(pools)
                    concat_inputs = pools
                self.concat_l2 = tf.concat(self.poolss[-1], 1, name="Convnet_Concat")
                concat_l2_dim = int(self.concat_l2.shape[-1]) * int(self.concat_l2.shape[-2])
                self.concat_out = tf.reshape(self.concat_l2,
                                             shape=[self.step_num, -1, concat_l2_dim])
            with tf.name_scope("Dropout") as scope:
                self.dropout_keep_prob = tf.placeholder(tf.float32, name="Dropout_Keep_Probability")
                self.dropout = tf.nn.dropout(self.concat_out, self.dropout_keep_prob)
            with tf.name_scope("Linear1") as scope:
                self.linear1 = tf.layers.dense(self.dropout, self.linear1_sz)
                self.relu = tf.nn.relu(self.linear1)
            with tf.name_scope("LSTM") as scope:
                self.lstm = tf.contrib.rnn.BasicLSTMCell(self.lstm_sz)
                self.state = [tf.placeholder(tf.float32, shape=[None, self.lstm.state_size[0]], name="LSTM_State_C"),
                              tf.placeholder(tf.float32, shape=[None, self.lstm.state_size[1]], name="LSTM_State_H")]
                state = self.state
                for step in range(self.step_num):
                    with tf.variable_scope("Step", reuse=True if step > 0 else None):
                        lstm_output, new_state = self.lstm(self.relu[step, :], state)
                        state = new_state
                    self.new_state = new_state
                    self.lstm_output = lstm_output
            with tf.name_scope("Linear2") as scope:
                self.linear2 = tf.layers.dense(self.lstm_output, self.linear2_sz)
                self.relu2 = tf.nn.relu(self.linear2)
            with tf.name_scope("Output") as scope:
                self.logits = tf.layers.dense(self.relu2, self.label_num, name="Logits")
                with tf.name_scope("Loss") as sub_scope:
                    self.loss = tf.reduce_sum(
                        tf.nn.softmax_cross_entropy_with_logits(labels=self.train_labels, logits=self.logits))
                    tf.summary.scalar('loss', self.loss)

                    with tf.name_scope("Accuracy") as sub_scope:
                        self.predictions = tf.equal(tf.argmax(self.logits, -1), tf.argmax(self.train_labels, -1))
                        with tf.name_scope("Train") as sub_scope2:
                            self.train_accuracy = tf.reduce_mean(tf.cast(self.predictions, "float"),
                                                                 name="Train_Accuracy")
                            tf.summary.scalar("Train Accuracy", self.train_accuracy)
                        with tf.name_scope("Valid") as sub_scope2:
                            self.valid_accuracy = tf.reduce_mean(
                                tf.cast(self.predictions, "float"), name="Valid_Accuracy")
                            tf.summary.scalar("Valid Accuracy", self.valid_accuracy)
                        with tf.name_scope("Test") as sub_scope2:
                            self.test_accuracy = tf.reduce_mean(
                                tf.cast(self.predictions, "float"), name="Test_Accuracy")
                            tf.summary.scalar("Test Accuracy", self.valid_accuracy)

            with tf.name_scope("Optimizer") as scope:
                self.optimizer = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)
                # self.optimizer = tf.train.GradientDescentOptimizer(Mes.PRE_E_FIXED_RATE).minimize(self.loss)

            self.saver = tf.train.Saver()
            self.merge_all = tf.summary.merge_all()
