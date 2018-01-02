# -*- coding: utf-8 -*-
import random
import numpy

import text_extractor
import mes_holder
import utils
import word2vec


class DataGenerator(object):
    def __init__(self, mes, trainable=True, truncated=False):
        self.mes = mes
        self.col_name = mes.train_col
        self.trainable = trainable
        self.truncated = truncated
        self.lang = self.mes.config['LANG']
        self.fids = self.mes.config['DG_FIDS']
        self.sentence_sz = self.mes.config['DG_SENTENCE_SZ']
        self.label_num = self.mes.config['LABEL_NUM']
        self.batch_sz = self.mes.config['DG_BATCH_SZ']
        self.test_batch_sz = self.mes.config['DG_TEST_BATCH_SZ']
        self.rnum = self.mes.config['DG_RNUM']
        self.w2v = word2vec.Word2Vec(self.mes, trainable=False)
        print("Train mode:", trainable)
        if trainable and self.col_name is not None:
            self.fold_num = self.mes.config['DG_FOLD_NUM']
            self.fold_test_id = self.mes.config['DG_FOLD_TEST_ID']
            self.fold_valid_id = self.mes.config['DG_FOLD_VALID_ID']
            self.docs = utils.get_docs(self.col_name)
            records = self.docs.find()
            records = [record for record in records]
            self.test_data, self.test_labels = DataGenerator.get_data_by_fold_ids(records, [self.fold_test_id])
            self.valid_data, self.valid_labels = DataGenerator.get_data_by_fold_ids(records, [self.fold_valid_id])
            self.train_data, self.train_labels = \
                DataGenerator.get_data_by_fold_ids(
                    records, [i for i in range(self.fold_num)
                              if i != self.fold_test_id and i != self.fold_valid_id])

            self.test_sz = len(self.test_data)
            self.valid_sz = len(self.valid_data)
            self.train_sz = len(self.train_data)
            self.test_inds = [0, 0, 0]
            self.valid_inds = [0, 0, 0]
            self.train_inds = [0, 0, self.rnum]
        elif not trainable:
            self.cutter = text_extractor.parser_holder.get_parser()

    @staticmethod
    def get_data_by_fold_ids(records, fold_ids=None):
        labels = [record['tag'] for record in records
                  if (fold_ids is not None and record["fold_id"] in fold_ids)]
        dataset = [record['words'] for record in records
                   if (fold_ids is not None and record["fold_id"] in fold_ids)]
        dataset, labels = DataGenerator.shuffle(dataset, labels)
        return dataset, labels

    def text2vec(self, text, lang):
        words = self.cutter.split(text, lang)
        words = self.w2v.delete_rare_words_single(words, nature_filter=word2vec.Word2Vec.nature_filter)
        ans = []
        fl = False
        inds = [0, 0, 0]
        while not fl:
            batch, _, fl = self.next([words], [0], inds, 1, 1)
            ans.append(batch)
        return {'batches': ans, 'words': words}

    def words2vec(self, words, ind):
        ans = {}
        ind_end = min(len(words), ind + self.sentence_sz)
        for fid in self.fids:
            ans[fid] = [0] * self.sentence_sz
            for i in range(ind, ind_end):
                if words[i][fid] is not None:
                    if fid in self.w2v.one_hot_fids:
                        ans[fid][i - ind] = self.w2v.features_ids[fid].get(words[i][fid], 0) + 1
                    else:
                        ans[fid][i - ind] = words[i][fid]
        return ans

    def label2vec(self, label=None, ind=None):
        ans = [0] * self.label_num
        if label is None:
            return ans
        ans[label + 1] = 1
        return ans

    @staticmethod
    def shuffle(data2shuffle, labels2shuffle):
        # print("Shuffled!")
        zp = zip(data2shuffle, labels2shuffle)
        random.shuffle(zp)
        return [ele[0] for ele in zp], [ele[1] for ele in zp]

    def next(self, data, labels, inds, batch_sz, r_num=0):
        # print(inds)
        # assert self.trainable
        assert(len(data) == len(labels))
        data_ind, word_ind = inds[:2]
        data_sz = len(data)
        ans = {}
        for fid in self.fids:
            ans[fid] = []
        new_labels = []
        fl = True
        for data_ind in range(inds[0], inds[0] + batch_sz):
            words = data[data_ind % data_sz]
            label = labels[data_ind % data_sz]
            vec = self.words2vec(words, word_ind)
            for fid in self.fids:
                ans[fid].append(vec[fid])
            new_labels.append(self.label2vec(label, word_ind))
            if not self.truncated and word_ind + self.sentence_sz < len(words):
                fl = False
        if fl:
            if inds[2] == 0:
                inds[0] = (inds[0] + batch_sz) % data_sz
                inds[2] = r_num
            else:
                inds[2] -= 1
            inds[1] = 0
        else:
            inds[1] += self.sentence_sz
        for fid in self.fids:
            ans[fid] = numpy.array(ans[fid])
        return ans, numpy.array(new_labels), fl

    def next_test(self):
        return self.next(self.test_data, self.test_labels, self.test_inds, self.test_batch_sz)

    def next_valid(self):
        return self.next(self.valid_data, self.valid_labels, self.valid_inds, self.test_batch_sz)

    def next_train(self, batch_sz=None, rnum=0):
        if batch_sz is None:
            batch_sz = self.batch_sz
        nxt = self.next(self.train_data, self.train_labels, self.train_inds, batch_sz, rnum)
        if self.train_inds[0] < self.batch_sz and self.train_inds[1] == 0 and self.train_inds[2] == rnum:
            self.train_data, self.train_labels = DataGenerator.shuffle(self.train_data, self.train_labels)
        return nxt


if __name__ == '__main__':
    mes = mes_holder.Mes("nlpcc_zh", "NOLSTM", "web")
    dg = DataGenerator(mes, trainable=False)
    ans = dg.text2vec(u'我今天有点不太高兴', 'zh')
