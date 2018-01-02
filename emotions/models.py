# class ABSALSTMModel(object):
#     def __init__(self, mes, graph):
#         self.mes = mes
#         self.graph = graph
#         self.step_num = mes.config['DG_STEP_NUM']
#         self.sentence_sz = self.mes.config['DG_SENTENCE_SZ']
#         self.label_num = mes.config['LABEL_NUM']
#         self.c_fids = mes.config['PRE_C_FIDS']
#         self.emb_fids = mes.config['PRE_EMB_FIDS']
#         for fid in self.emb_fids:
#             assert(fid in mes.config['W2V_TRAIN_FIDS'])
#         self.one_hot_fids = mes.config['PRE_ONE_HOT_FIDS']
#         self.one_hot_depths = mes.config['PRE_ONE_HOT_DEPTHS']
#         self.convs_l1_kernel_num = mes.config['PRE_CONVS_L1_KERNEL_NUM']
#         self.convs_l1_stride = mes.config['PRE_CONVS_L1_STRIDE']
#         self.convs_l1_filter_num = mes.config['PRE_CONV_L1_FILTER_NUM']
#         self.pools_l1_size = mes.config['PRE_POOLS_L1_SIZE']
#         self.pools_l1_stride = mes.config['PRE_POOLS_L1_STRIDE']
#         self.convs_l2_kernel_num = mes.config['PRE_CONVS_L2_KERNEL_NUM']
#         self.convs_l2_stride = mes.config['PRE_CONVS_L2_STRIDE']
#         self.convs_l2_filter_num = mes.config['PRE_CONV_L2_FILTER_NUM']
#         self.pools_l2_size = mes.config['PRE_POOLS_L2_SIZE']
#         self.pools_l2_stride = mes.config['PRE_POOLS_L2_STRIDE']
#         self.linear1_sz = mes.config['PRE_LINEAR1_SZ']
#         self.lstm_sz = mes.config['PRE_LSTM_SZ']
#         self.linear2_sz = mes.config['PRE_LINEAR2_SZ']
#         self.learning_rate = mes.config['PRE_E_LEARNING_RATE']
#
#         assert(len(self.one_hot_fids) == len(self.one_hot_depths))
#         self.fids = set(self.c_fids + self.emb_fids + self.one_hot_fids)
#         for fid in self.fids:
#             assert(fid in mes.config['DG_FIDS'])
#         with self.graph.as_default():
#             # input_value
#             with tf.name_scope("Input") as scope:
#                 self.train_dataset = {}
#                 for fid in self.fids:
#                     if fid in self.c_fids:
#                         self.train_dataset[fid] = tf.placeholder(tf.float32,
#                                                                  shape=[self.step_num, None, self.sentence_sz],
#                                                                  name="DataBatch_{}".format(fid))
#                     else:
#                         self.train_dataset[fid] = tf.placeholder(tf.int32,
#                                                                  shape=[self.step_num, None, self.sentence_sz],
#                                                                  name="DataBatch_{}".format(fid))
#                 self.train_labels = tf.placeholder(tf.int32, shape=[None, self.label_num], name="Label")
#             # variable
#             with tf.name_scope("One_hot") as scope:
#                 self.one_hots = []
#                 for fid, depth in zip(self.one_hot_fids, self.one_hot_depths):
#                     self.one_hots.append(tf.to_float(tf.one_hot(self.train_dataset[fid], depth=depth, axis=-1,
#                                                                 dtype=tf.int32, name="One_hot_{}".format(fid))))
#             with tf.name_scope("Embedding") as scope:
#                 self.embeddings = {}
#                 self.embeds = []
#                 for fid in self.emb_fids:
#                     with open(mes.get_feature_emb_path(fid)) as fin:
#                         init_embedding = json.load(fin)
#                     self.embeddings[fid] = tf.Variable(init_embedding, name="Embedding_{}".format(fid))
#                     # model
#                     self.embeds.append(tf.nn.embedding_lookup(self.embeddings[fid], self.train_dataset[fid],
#                                                               name="Embed_{}".format(fid)))
#             with tf.name_scope("Continuous_Feature") as scope:
#                 self.cfeatures = []
#                 for fid in self.c_fids:
#                     self.cfeatures.append(tf.expand_dims(self.train_dataset[fid], -1,
#                                                          "Continuous_Feature_{}".format(fid)))
#             with tf.name_scope("Concat") as scope:
#                 self.concat_input = tf.concat(self.embeds + self.one_hots + self.cfeatures, -1)
#                 concat_input_dim = int(self.concat_input.shape[-1])
#                 print concat_input_dim
#                 self.concat_reshape = tf.reshape(self.concat_input, shape=[-1, self.sentence_sz, concat_input_dim])
#             with tf.name_scope("Convnet") as scope:
#                 self.convs_l1 = []
#                 self.pools_l1 = []
#                 self.convs_l2 = []
#                 self.pools_l2 = []
#                 for conv_knum, conv_stride, pool_size, pool_stride in zip(self.convs_l1_kernel_num,
#                                                                           self.convs_l1_stride,
#                                                                           self.pools_l1_size,
#                                                                           self.pools_l1_stride):
#                     conv = tf.layers.conv1d(self.concat_reshape, self.convs_l1_filter_num, conv_knum, conv_stride,
#                                             use_bias=True, activation=tf.nn.relu, padding="same")
#                     pool = tf.layers.max_pooling1d(conv, pool_size, pool_stride, padding="same")
#                     self.convs_l1.append(conv)
#                     self.pools_l1.append(pool)
#                     for conv2_knum, conv2_stride, pool2_size, pool2_stride in zip(self.convs_l2_kernel_num,
#                                                                                   self.convs_l2_stride,
#                                                                                   self.pools_l2_size,
#                                                                                   self.pools_l2_stride):
#                         conv2 = tf.layers.conv1d(pool, self.convs_l2_filter_num, conv2_knum, conv2_stride,
#                                                  use_bias=True, activation=tf.nn.relu, padding="same")
#                         pool2 = tf.layers.max_pooling1d(conv2, pool2_size, pool2_stride, padding="same")
#                         self.convs_l2.append(conv2)
#                         self.pools_l2.append(pool2)
#                 self.concat_l2 = tf.concat(self.pools_l2, 1, name="Convnet_Concat_Level2")
#                 concat_l2_dim = int(self.concat_l2.shape[-1]) * int(self.concat_l2.shape[-2])
#                 print concat_l2_dim
#                 self.concat_out = tf.reshape(self.concat_l2,
#                                              shape=[self.step_num, -1, concat_l2_dim])
#             with tf.name_scope("Dropout") as scope:
#                 self.dropout_keep_prob = tf.placeholder(tf.float32, name="Dropout_Keep_Probability")
#                 self.dropout = tf.nn.dropout(self.concat_out, self.dropout_keep_prob)
#             with tf.name_scope("Linear1") as scope:
#                 self.linear1 = tf.layers.dense(self.dropout, self.linear1_sz)
#                 self.relu = tf.nn.relu(self.linear1)
#             with tf.name_scope("LSTM_Encoder") as scope:
#                 self.lstm_encoder = tf.contrib.rnn.BasicLSTMCell(self.lstm_sz)
#                 self.state_encoder = [tf.placeholder(tf.float32, shape=[None, self.lstm_encoder.state_size[0]],
#                                                      name="LSTM_Encoder_State_C"),
#                                       tf.placeholder(tf.float32, shape=[None, self.lstm_encoder.state_size[1]],
#                                                      name="LSTM_Encoder_State_H")]
#                 state_encoder = self.state_encoder
#                 for step in range(self.step_num):
#                     with tf.variable_scope("Step_Encoder", reuse=True if step > 0 else None):
#                         lstm_tmp_output_encoder, new_state_encoder = self.lstm_encoder(self.relu[step, :],
#                                                                                        state_encoder)
#                         state_encoder = new_state_encoder
#                     if step == self.step_num - 1:
#                         self.new_state_encoder = new_state_encoder
#                         self.lstm_output_encoder = tf.concat([sub_state for sub_state in self.new_state_encoder], -1)
#             with tf.name_scope("Attention") as scope:
#                 self.attention = tf.layers.dense(self.lstm_output_encoder, self.lstm_sz)
#                 self.attention_output = tf.nn.softmax(self.attention)
#             with tf.name_scope("LSTM_Decoder") as scope:
#                 self.lstm_decoder = tf.contrib.rnn.BasicLSTMCell(self.lstm_sz)
#                 self.state_decoder = [tf.placeholder(tf.float32, shape=[None, self.lstm_decoder.state_size[0]],
#                                                      name="LSTM_Decoder_State_C"),
#                                       tf.placeholder(tf.float32, shape=[None, self.lstm_decoder.state_size[1]],
#                                                      name="LSTM_Decoder_State_H")]
#                 self.lstm_decoder_past = tf.placeholder(tf.float32, shape=[None, self.label_num], name="Last_Label")
#                 self.lstm_decoder_input = tf.concat([self.lstm_decoder_past, self.attention_output],
#                                                     axis=-1, name="Decoder_Input")
#                 self.lstm_output_decoder, self.new_state_decoder = self.lstm_decoder(self.lstm_decoder_input,
#                                                                                      self.state_decoder)
#             with tf.name_scope("Linear2") as scope:
#                 self.linear2 = tf.layers.dense(self.lstm_output_decoder, self.linear2_sz)
#                 self.relu2 = tf.nn.relu(self.linear2)
#             with tf.name_scope("Output") as scope:
#                 self.logits = tf.layers.dense(self.relu2, self.label_num, name="Logits")
#             with tf.name_scope("Loss") as sub_scope:
#                 self.loss = tf.reduce_sum(
#                     tf.nn.softmax_cross_entropy_with_logits(labels=self.train_labels, logits=self.logits))
#                 tf.summary.scalar('loss', self.loss)
#                 with tf.name_scope("Accuracy") as sub_scope:
#                     self.predictions = tf.equal(tf.argmax(self.logits, -1), tf.argmax(self.train_labels, -1))
#                     with tf.name_scope("Train") as sub_scope2:
#                         self.train_accuracy = tf.reduce_mean(tf.cast(self.predictions, "float"),
#                                                                  name="Train_Accuracy")
#                         tf.summary.scalar("Train Accuracy", self.train_accuracy)
#                     with tf.name_scope("Valid") as sub_scope2:
#                         self.valid_accuracy = tf.reduce_mean(
#                             tf.cast(self.predictions, "float"), name="Valid_Accuracy")
#                         tf.summary.scalar("Valid Accuracy", self.valid_accuracy)
#                     with tf.name_scope("Test") as sub_scope2:
#                         self.test_accuracy = tf.reduce_mean(
#                             tf.cast(self.predictions, "float"), name="Test_Accuracy")
#                         tf.summary.scalar("Test Accuracy", self.valid_accuracy)
#
#             with tf.name_scope("Optimizer") as scope:
#                 self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.loss)
#                 # self.optimizer = tf.train.GradientDescentOptimizer(Mes.PRE_E_FIXED_RATE).minimize(self.loss)
#
#             self.saver = tf.train.Saver()
#             self.merge_all = tf.summary.merge_all()
#
#
# class ABSANOLSTMModel(object):
#     def __init__(self, mes, graph):
#         self.mes = mes
#         self.graph = graph
#         self.sentence_sz = self.mes.config['DG_SENTENCE_SZ']
#         self.label_num = self.mes.config['LABEL_NUM']
#         self.c_fids = mes.config['PRE_C_FIDS']
#         self.emb_fids = mes.config['PRE_EMB_FIDS']
#         for fid in self.emb_fids:
#             assert(fid in mes.config['W2V_TRAIN_FIDS'])
#         self.one_hot_fids = mes.config['PRE_ONE_HOT_FIDS']
#         self.one_hot_depths = mes.config['PRE_ONE_HOT_DEPTHS']
#         self.convs_level_nums = mes.config['PRE_CONVS_LEVEL_NUMS']
#         self.convs_kernel_nums = mes.config['PRE_CONVS_KERNEL_NUMS']
#         self.convs_strides = mes.config['PRE_CONVS_STRIDES']
#         self.convs_filter_nums = mes.config['PRE_CONVS_FILTER_NUMS']
#         self.pools_sizes = mes.config['PRE_POOLS_SIZES']
#         self.pools_strides = mes.config['PRE_POOLS_STRIDES']
#         self.linear1_sz = mes.config['PRE_LINEAR1_SZ']
#         self.linear2_sz = mes.config['PRE_LINEAR2_SZ']
#         self.learning_rate = mes.config['PRE_E_LEARNING_RATE']
#
#         assert(len(self.one_hot_fids) == len(self.one_hot_depths))
#         self.fids = set(self.c_fids + self.emb_fids + self.one_hot_fids)
#         for fid in self.fids:
#             assert(fid in mes.config['DG_FIDS'])
#         with self.graph.as_default():
#             # input_value
#             with tf.name_scope("Input") as scope:
#                 self.train_dataset = {}
#                 for fid in self.fids:
#                     if fid in self.c_fids:
#                         self.train_dataset[fid] = tf.placeholder(tf.float32, shape=[None, self.sentence_sz],
#                                                                  name="DataBatch_{}".format(fid))
#                     else:
#                         self.train_dataset[fid] = tf.placeholder(tf.int32, shape=[None, self.sentence_sz],
#                                                                  name="DataBatch_{}".format(fid))
#                 # self.batch_size = tf.shape(self.train_dataset)[0]
#                 self.train_labels = tf.placeholder(tf.int32, shape=[None, self.sentence_sz, self.label_num],
#                                                    name="Label")
#             # variable
#             with tf.name_scope("One_hot") as scope:
#                 self.one_hots = []
#                 for fid, depth in zip(self.one_hot_fids, self.one_hot_depths):
#                     self.one_hots.append(tf.to_float(tf.one_hot(self.train_dataset[fid], depth=depth, axis=-1,
#                                                                 dtype=tf.int32, name="One_hot_{}".format(fid))))
#             with tf.name_scope("Embedding") as scope:
#                 self.embeddings = {}
#                 self.embeds = []
#                 for fid in self.emb_fids:
#                     with open(mes.get_feature_emb_path(fid)) as fin:
#                         init_embedding = json.load(fin)
#                     self.embeddings[fid] = tf.Variable(init_embedding, name="Embedding_{}".format(fid))
#                     # model
#                     self.embeds.append(tf.nn.embedding_lookup(self.embeddings[fid], self.train_dataset[fid],
#                                                               name="Embed_{}".format(fid)))
#             with tf.name_scope("Continuous_Feature") as scope:
#                 self.cfeatures = []
#                 for fid in self.c_fids:
#                     self.cfeatures.append(tf.expand_dims(self.train_dataset[fid], -1,
#                                                          "Continuous_Feature_{}".format(fid)))
#             with tf.name_scope("Concat") as scope:
#                 self.concat_input = tf.concat(self.embeds + self.one_hots + self.cfeatures, -1)
#             with tf.name_scope("Convnet") as scope:
#                 self.convss = []
#                 self.poolss = []
#                 concat_inputs = [self.concat_input]
#                 for i in range(self.convs_level_nums):
#                     convs = []
#                     pools = []
#                     for conv_knum, conv_stride, pool_size, pool_stride in zip(self.convs_kernel_nums[i],
#                                                                               self.convs_strides[i],
#                                                                               self.pools_sizes[i],
#                                                                               self.pools_strides[i]):
#                         for input in concat_inputs:
#                             conv = tf.layers.conv1d(input, self.convs_filter_nums[i], conv_knum, conv_stride,
#                                                     use_bias=True, activation=tf.nn.relu, padding="same")
#                             if pool_size == -1 or pool_stride == -1:
#                                 pool_size = pool_stride = int(conv.shape[-2])
#                             pool = tf.layers.max_pooling1d(conv, pool_size, pool_stride, padding="same")
#                             convs.append(conv)
#                             pools.append(pool)
#                     self.convss.append(convs)
#                     self.poolss.append(pools)
#                     concat_inputs = pools
#                 self.concat_l2 = tf.concat(self.poolss[-1], 1, name="Convnet_Concat")
#             with tf.name_scope("Dropout") as scope:
#                 shape = self.concat_l2.get_shape().as_list()
#                 out_num = shape[1] * shape[2]
#                 self.reshaped = tf.reshape(self.concat_l2, [-1, out_num])
#                 self.dropout_keep_prob = tf.placeholder(tf.float32, name="Dropout_Keep_Probability")
#                 self.dropout = tf.nn.dropout(self.reshaped, self.dropout_keep_prob)
#             with tf.name_scope("Linear1") as scope:
#                 self.linear1 = tf.layers.dense(self.dropout, self.linear1_sz)
#                 self.relu = tf.nn.relu(self.linear1)
#             with tf.name_scope("Linear2") as scope:
#                 self.linear2 = tf.layers.dense(self.relu, self.linear2_sz)
#                 self.relu2 = tf.nn.relu(self.linear2)
#             with tf.name_scope("Output") as scope:
#                 self.logits = tf.reshape(tf.layers.dense(self.relu2, self.label_num * self.sentence_sz,
#                                                          name="Logits"), shape=[-1, self.sentence_sz, self.label_num])
#                 with tf.name_scope("Loss") as sub_scope:
#                     self.loss = tf.reduce_sum(
#                         tf.nn.softmax_cross_entropy_with_logits(labels=self.train_labels, logits=self.logits))
#                     tf.summary.scalar('loss', self.loss)
#
#                     with tf.name_scope("Accuracy") as sub_scope:
#                         self.predictions = tf.equal(tf.argmax(self.logits, -1), tf.argmax(self.train_labels, -1))
#                         with tf.name_scope("Train") as sub_scope2:
#                             self.train_accuracy = tf.reduce_mean(tf.cast(self.predictions, "float"),
#                                                                  name="Train_Accuracy")
#                             tf.summary.scalar("Train Accuracy", self.train_accuracy)
#                         with tf.name_scope("Valid") as sub_scope2:
#                             self.valid_accuracy = tf.reduce_mean(
#                                 tf.cast(self.predictions, "float"), name="Valid_Accuracy")
#                             tf.summary.scalar("Valid Accuracy", self.valid_accuracy)
#                         with tf.name_scope("Test") as sub_scope2:
#                             self.test_accuracy = tf.reduce_mean(
#                                 tf.cast(self.predictions, "float"), name="Test_Accuracy")
#                             tf.summary.scalar("Test Accuracy", self.valid_accuracy)
#
#             with tf.name_scope("Optimizer") as scope:
#                 self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate).minimize(self.loss)
#                 # self.optimizer = tf.train.GradientDescentOptimizer(Mes.PRE_E_FIXED_RATE).minimize(self.loss)
#
#             self.saver = tf.train.Saver()
#             self.merge_all = tf.summary.merge_all()
