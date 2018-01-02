import numpy
import sys

import predictor
import mes_holder
import scripts


class PredictorABSALSTM(predictor.Predictor):
    def __init__(self, col_name, model_name, trainable=True):
        mes = mes_holder.Mes(col_name, "ABSA_LSTM", model_name=model_name)
        super(PredictorABSALSTM, self).__init__(mes, trainable)

    def train_sentences(self, session, nxt_method, batch_sz):
        batch_data, batch_labels, finished = nxt_method(batch_sz)
        batch_len = min(len(batch_labels), self.data_generator.sentence_sz)
        state_encoder = [numpy.zeros([batch_sz, sz], dtype=float) for sz in self.model.lstm_encoder.state_size]
        feed_dict = {self.model.dropout_keep_prob: self.dropout_keep_prob_rate}

        while True:
            state_decoder = [numpy.zeros([batch_sz, sz], dtype=float) for sz in self.model.lstm_decoder.state_size]
            for i in range(2):
                feed_dict[self.model.state_encoder[i].name] = state_encoder[i]
            for fid in self.data_generator.fids:
                feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
            accuracies = []
            loss = 0
            for word_ind in range(batch_len):
                for i in range(2):
                    feed_dict[self.model.state_decoder[i].name] = state_decoder[i]
                if word_ind == 0:
                    feed_dict[self.model.lstm_decoder_past] = numpy.zeros([batch_sz, self.data_generator.label_num])
                else:
                    feed_dict[self.model.lstm_decoder_past] = batch_labels[word_ind - 1]
                feed_dict[self.model.train_labels] = batch_labels[word_ind]

                _, new_state_encoder, new_state_decoder, sub_loss, accuracy = session.run(
                    [self.model.optimizer, self.model.new_state_encoder,
                     self.model.new_state_decoder, self.model.loss, self.model.train_accuracy], feed_dict=feed_dict)
                state_encoder = new_state_encoder
                state_decoder = new_state_decoder
                loss += sub_loss
                accuracies.append(accuracy)
            print accuracies
            if finished:
                return loss, numpy.mean(accuracies)
            else:
                batch_data, batch_labels, finished = nxt_method(batch_sz)
                batch_len += self.data_generator.sentence_sz

    def test_sentences(self, session, nxt_method, is_valid=True):
        batch_data, batch_labels, finished = nxt_method()
        model_accuracy = self.model.valid_accuracy if is_valid else self.model.test_accuracy
        batch_len = min(len(batch_labels), self.data_generator.sentence_sz)
        state_encoder = [numpy.zeros([self.data_generator.test_batch_sz, sz], dtype=float)
                         for sz in self.model.lstm_encoder.state_size]
        feed_dict = {self.model.dropout_keep_prob: self.dropout_keep_prob_rate}

        while not finished:
            state_decoder = [numpy.zeros([self.data_generator.test_batch_sz, sz], dtype=float)
                             for sz in self.model.lstm_decoder.state_size]
            for i in range(2):
                feed_dict[self.model.state_encoder[i].name] = state_encoder[i]
            for fid in self.data_generator.fids:
                feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
            accuracies = []
            loss = 0
            for word_ind in range(batch_len):
                for i in range(2):
                    feed_dict[self.model.state_decoder[i].name] = state_decoder[i]
                if word_ind == 0:
                    feed_dict[self.model.lstm_decoder_past] = numpy.zeros([self.data_generator.test_batch_sz,
                                                                          self.data_generator.label_num])
                feed_dict[self.model.train_labels] = batch_labels[word_ind]

                new_state_encoder, new_state_decoder, sub_loss, accuracy, logits = session.run(
                    [self.model.new_state_encoder, self.model.new_state_decoder,
                     self.model.loss, model_accuracy, self.model.logits], feed_dict=feed_dict)
                state_encoder = new_state_encoder
                state_decoder = new_state_decoder
                loss += sub_loss
                accuracies.append(accuracy)
                feed_dict[self.model.lstm_decoder_past] = logits
            print accuracies
            if finished:
                return numpy.mean(accuracies)
            else:
                batch_data, batch_labels, finished = nxt_method()

    def predict(self, text):
        batches = self.data_generator.text2vec(text)
        feed_dict = {self.model.dropout_keep_prob: 1.0}
        state = [numpy.zeros([1, sz], dtype=float) for sz in self.model.lstm.state_size]
        logits = None
        for batch_data in batches:
            for i in range(2):
                feed_dict[self.model.state[i].name] = state[i]
            for fid in self.data_generator.fids:
                feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
            logits, new_state = self.session.run([self.model.logits, self.model.new_state], feed_dict=feed_dict)
            state = new_state
        return logits[0]

if __name__ == '__main__':
    scripts.run()
