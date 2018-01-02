import predictor
import mes_holder
import sys
import scripts


class PredictorABSANOLSTM(predictor.Predictor):
    def __init__(self, col_name, model_name, trainable=True):
        mes = mes_holder.Mes(col_name, "ABSA_NOLSTM", model_name=model_name)
        super(PredictorABSANOLSTM, self).__init__(mes, trainable)

    def train_sentences(self, session, nxt_method, batch_sz):
        batch_data, batch_labels, finished = nxt_method(batch_sz)
        feed_dict = {self.model.dropout_keep_prob: self.dropout_keep_prob_rate,
                     self.model.train_labels: batch_labels}
        for fid in self.data_generator.fids:
            feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
        _, loss, accuracy = session.run(
            [self.model.optimizer, self.model.loss, self.model.train_accuracy], feed_dict=feed_dict)
        return loss, accuracy

    def test_sentences(self, session, nxt_method, is_valid=True):
        model_accuracy = self.model.valid_accuracy if is_valid else self.model.test_accuracy
        batch_data, batch_labels, finished = nxt_method()
        feed_dict = {self.model.dropout_keep_prob: 1.0, self.model.train_labels: batch_labels}
        for fid in self.data_generator.fids:
            feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
        accuracy = session.run([model_accuracy], feed_dict=feed_dict)[0]
        return accuracy

    def predict(self, text):
        batches = self.data_generator.text2vec(text)
        feed_dict = {self.model.dropout_keep_prob: 1.0}
        for fid in self.data_generator.fids:
            feed_dict[self.model.train_dataset[fid]] = batches[0][fid]
        logits = self.session.run([self.model.logits], feed_dict=feed_dict)[0]
        return logits[0]


if __name__ == '__main__':
    scripts.run()