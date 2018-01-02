# -*- coding: utf-8 -*-
import predictor
import mes_holder
import scripts
import utils


class PredictorNOLSTM(predictor.Predictor):
    def __init__(self, col_name, model_name, trainable=True):
        mes = mes_holder.Mes(col_name, "NOLSTM", model_name=model_name)
        super(PredictorNOLSTM, self).__init__(mes, trainable)

    def train_sentences(self, session, nxt_method, batch_sz):
        batch_data, batch_labels, finished = nxt_method(batch_sz)
        feed_dict = {self.model.dropout_keep_prob: self.dropout_keep_prob_rate,
                     self.model.train_labels: batch_labels}
        for fid in self.data_generator.fids:
            feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
        summary, _, loss, accuracy = session.run(
            [self.model.merge_all, self.model.optimizer, self.model.loss, self.model.train_accuracy], feed_dict=feed_dict)
        self.writer.add_summary(summary)
        return loss, accuracy

    def test_sentences(self, session, nxt_method, is_valid=True):
        model_accuracy = self.model.valid_accuracy if is_valid else self.model.test_accuracy
        batch_data, batch_labels, finished = nxt_method()
        feed_dict = {self.model.dropout_keep_prob: 1.0, self.model.train_labels: batch_labels}
        for fid in self.data_generator.fids:
            feed_dict[self.model.train_dataset[fid]] = batch_data[fid]
        summary, accuracy = session.run([self.model.merge_all, model_accuracy], feed_dict=feed_dict)
        self.writer.add_summary(summary)
        return accuracy

    def predict(self, text):
        resp = self.data_generator.text2vec(text, self.mes.lang)
        batches = resp['batches']
        resp.pop('batches')
        feed_dict = {self.model.dropout_keep_prob: 1.0}
        for fid in self.data_generator.fids:
            feed_dict[self.model.train_dataset[fid]] = batches[0][fid]
        logits = self.session.run([self.model.logits], feed_dict=feed_dict)[0]
        resp['tag'] = utils.get_tag_from_logits(logits[0])
        return resp


if __name__ == '__main__':
    # predictor = PredictorNOLSTM('ctrip', 'web', trainable=False)
    # predictor.predict(u'我有点小生气')
    scripts.run()

