import predictor
import mes_holder
import numpy
import scripts
import utils


class PredictorLSTM(predictor.Predictor):
    def __init__(self, col_name, model_name, trainable=True):
        mes = mes_holder.Mes(col_name, "LSTM", model_name=model_name)
        super(PredictorLSTM, self).__init__(mes, trainable)

    def train_sentences(self, session, nxt_method, batch_sz):
        batch_data, batch_labels, finished = nxt_method(batch_sz)
        state = [numpy.zeros([batch_sz, sz], dtype=float) for sz in self.model.lstm.state_size]
        feed_dict = {self.model.dropout_keep_prob: self.dropout_keep_prob_rate}
        while True:
            for i in range(2):
                feed_dict[self.model.state[i].name] = state[i]
            for fid in self.data_generator.fids:
                feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
            feed_dict[self.model.train_labels] = batch_labels
            if not finished:
                _, loss, new_state = session.run(
                    [self.model.optimizer, self.model.loss, self.model.new_state], feed_dict=feed_dict)
            else:
                concet, dataset, summary, _, loss, accuracy = session.run(
                    [self.model.train_dataset,self.model.concat_reshape, self.model.merge_all, self.model.optimizer, self.model.loss, self.model.train_accuracy],
                    feed_dict=feed_dict)
                self.writer.add_summary(summary)
                return loss, accuracy
            batch_data, batch_labels, finished = nxt_method(batch_sz)
            state = new_state

    def test_sentences(self, session, nxt_method, is_valid=True):
        batch_data, batch_labels, finished = nxt_method()
        model_accuracy = self.model.valid_accuracy if is_valid else self.model.test_accuracy
        state = [numpy.zeros([self.data_generator.test_batch_sz, sz], dtype=float) for sz in self.model.lstm.state_size]
        feed_dict = {self.model.dropout_keep_prob: 1.0}
        while True:
            for i in range(2):
                feed_dict[self.model.state[i].name] = state[i]
            for fid in self.data_generator.fids:
                feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
            feed_dict[self.model.train_labels] = batch_labels
            if finished:
                summary, new_state, accuracy = session.run([self.model.merge_all, self.model.new_state, model_accuracy],
                                                           feed_dict=feed_dict)
                self.writer.add_summary(summary)
                return accuracy
            else:
                new_state = session.run([self.model.new_state], feed_dict=feed_dict)[0]
            batch_data, batch_labels, finished = nxt_method()
            state = new_state

    def predict(self, text):
        resp = self.data_generator.text2vec(text, self.mes.lang)
        batches = resp['batches']
        resp.pop('batches')
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
        resp['tag'] = utils.get_tag_from_logits(logits[0])
        return resp

if __name__ == '__main__':
    scripts.run()
