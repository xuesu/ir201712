import numpy

import data_generator
import mes_holder
import utils


class DataGeneratorABSALSTM(data_generator.DataGenerator):
    def __init__(self, mes, trainable=True):
        super(DataGeneratorABSALSTM, self).__init__(mes, trainable, truncated=True)
        self.step_num = mes.config['DG_STEP_NUM']
        self.label_num = mes.config['LABEL_NUM']
        self.tags_cache = None
        self.blocks_cache = []

    def label2vec(self, label=None, ind=None):
        ans = [0] * self.label_num
        if label is not None and ind < len(label):
            ans[label[ind] + 1] = 1
        else:
            ans[0] = 1
        return ans

    def next(self, data, labels, inds, batch_sz, r_num=0):
        assert self.trainable
        assert (len(data) == len(labels))
        data_ind, word_ind = inds[:2]
        data_sz = len(data)
        if len(self.blocks_cache) > 0:
            self.blocks_cache = self.blocks_cache[1:]
        fl = True
        max_words_len = 0
        while len(self.blocks_cache) < self.step_num:
            ans = {}
            for fid in self.fids:
                ans[fid] = []
            fl = True
            for data_ind in range(inds[0], inds[0] + batch_sz):
                words = data[data_ind % data_sz]
                max_words_len = max(max_words_len, len(words))
                vec = self.words2vec(words, word_ind)
                for fid in self.fids:
                    ans[fid].append(numpy.array(vec[fid]))
                if word_ind + self.sentence_sz < len(words):
                    fl = False
            inds[1] += self.sentence_sz
            word_ind = inds[1]
            self.blocks_cache.append(ans)

        if self.tags_cache is None:
            self.tags_cache = []
            for word_ind in range(max_words_len):
                sub_tags = []
                for data_ind in range(inds[0], inds[0] + batch_sz):
                    label = labels[data_ind % data_sz]
                    sub_tags.append(self.label2vec(label, max_words_len))
                self.tags_cache.append(sub_tags)
            self.tags_cache = numpy.array(self.tags_cache)

        tags = self.tags_cache
        blocks = {}
        for fid in self.fids:
            blocks[fid] = []
        for batch in self.blocks_cache:
            for fid in self.fids:
                blocks[fid].append(batch[fid])
        for fid in self.fids:
            blocks[fid] = numpy.array(blocks[fid])
        if fl:
            if inds[2] == 0:
                inds[0] = (inds[0] + batch_sz) % data_sz
                inds[2] = r_num
            else:
                inds[2] -= 1
            inds[1] = 0
            self.blocks_cache = []
            self.tags_cache = None

        return blocks, tags, fl


class DataGeneratorABSANOLSTM(data_generator.DataGenerator):
    def __init__(self, mes, trainable=True):
        super(DataGeneratorABSANOLSTM, self).__init__(mes, trainable, truncated=True)

    def label2vec(self, label=None, ind=None):
        ans = [[0] * self.label_num for _ in range(self.sentence_sz)]
        if label is None:
            return ans
        ind_end = min(len(label), ind + self.sentence_sz)
        for i in range(0, self.sentence_sz):
            if i + ind < ind_end:
                ans[i][label[i + ind] + 1] = 1
            else:
                ans[i][0] = 1
        return ans


if __name__ == '__main__':
    # mes = mes_holder.Mes("semval14_laptop", "Other", "W2V", "semval14.yml")
    # dg = DataGeneratorABSANOLSTM(mes)
    # # data, labels, finished = dg.next_train()
    # # for fid in data:
    # #     print data[fid].shape
    # #     print data[fid]
    # # print labels.shape
    # # print labels
    #
    # for i in range(50):
    #     print dg.test_inds
    #     batch_data, batch_labels, finished = dg.next_test()
    #     for fid in batch_data:
    #         print batch_data[fid][0]
    #     print 'label:', batch_labels[0]
    mes = mes_holder.Mes("semval14_laptop", "ABSA_LSTM", "Test")
    dg = DataGeneratorABSALSTM(mes)
    for i in range(50):
        print dg.test_inds
        batch_data, batch_labels, finished = dg.next_test()
        for fid in batch_data:
            print batch_data[fid].shape
            for batch_d in batch_data[fid]:
                print batch_d[0]
        print 'labels shape', batch_labels.shape
        print 'label:', batch_labels[0]
