# -*- coding: utf-8 -*-
import numpy

import data_generator
import mes_holder


class DataGeneratorLSTM(data_generator.DataGenerator):
    def __init__(self, mes, trainable=True):
        super(DataGeneratorLSTM, self).__init__(mes, trainable)
        self.step_num = mes.config['DG_STEP_NUM']
        self.step_back = mes.config['DG_STEP_BACK']
        self.blocks_cache = []

    def text2vec(self, text, lang):
        self.blocks_cache = []
        return super(DataGeneratorLSTM, self).text2vec(text, lang)

    def next(self, data, labels, inds, batch_sz, r_num=0):
        # print(inds)
        # assert self.trainable
        assert(len(data) == len(labels))
        data_sz = len(data)
        if len(self.blocks_cache) > 0:
            self.blocks_cache = self.blocks_cache[1:]
        fl = True
        while len(self.blocks_cache) < self.step_num:
            ans = {}
            for fid in self.fids:
                ans[fid] = []
            fl = True
            for data_ind in range(inds[0], inds[0] + batch_sz):
                words = data[data_ind % data_sz]
                vec = self.words2vec(words, inds[1])
                for fid in self.fids:
                    ans[fid].append(numpy.array(vec[fid]))
                if inds[1] + self.sentence_sz < len(words):
                    fl = False
            inds[1] += self.sentence_sz - self.step_back
            self.blocks_cache.append(ans)

        tags = []
        for data_ind in range(inds[0], inds[0] + batch_sz):
            label = labels[data_ind % data_sz]
            tags.append(self.label2vec(label, None))

        blocks = {}
        for fid in self.fids:
            blocks[fid] = []
        for batch in self.blocks_cache:
            for fid in self.fids:
                blocks[fid].append(batch[fid])
        if fl:
            if inds[2] == 0:
                inds[0] = (inds[0] + batch_sz) % data_sz
                inds[2] = r_num
            else:
                inds[2] -= 1
            inds[1] = 0
            self.blocks_cache = []
        return blocks, tags, fl


if __name__ == '__main__':
    mes = mes_holder.Mes("nlpcc_zh", "LSTM", "web")
    dg = DataGeneratorLSTM(mes, trainable=False)
    ans = dg.text2vec(u'我今天有点不太高兴', 'zh')
    print ans
