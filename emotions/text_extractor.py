# coding=utf-8
import jieba.posseg


class WordParser(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    @staticmethod
    def tokenize(unicode_sentence, mode="default", HMM=True):
        """
                Tokenize a sentence and yields tuples of (word, start, end)

                Parameter:
                    - sentence: the str(unicode) to be segmented.
                    - mode: "default" or "search", "search" is for finer segmentation.
                    - HMM: whether to use the Hidden Markov Model.
                """
        start = 0
        if mode == 'default':
            for w, pos in jieba.posseg.cut(unicode_sentence, HMM=HMM):
                width = len(w)
                yield (w, pos, start, start + width)
                start += width
        else:
            for w, pos in jieba.posseg.cut(unicode_sentence, HMM=HMM):
                width = len(w)
                if len(w) > 2:
                    for i in range(len(w) - 1):
                        gram2 = w[i:i + 2]
                        if jieba.posseg.dt.FREQ.get(gram2):
                            yield (gram2, pos, start + i, start + i + 2)
                if len(w) > 3:
                    for i in range(len(w) - 2):
                        gram3 = w[i:i + 3]
                        if jieba.posseg.dt.FREQ.get(gram3):
                            yield (gram3, pos, start + i, start + i + 3)
                yield (w, pos, start, start + width)
                start += width

    def split(self, text, lang='zh'):
        if lang == 'zh':
            return self.split_zh(text)
        raise NotImplementedError()

    def split_zh(self, text):
        # stop_nature_list = ['', 'w', 'x', 'y', 'c']
        # ans = [w[:2] for w in self.tokenize(text, mode='search') if w[1] not in stop_nature_list]
        ans = [list(w[:2]) for w in self.tokenize(text)]
        return ans


class WordParserHolder(object):
    def __init__(self):
        self.parser = None

    def get_parser(self):
        if self.parser is None:
            self.parser = WordParser()
        return self.parser


parser_holder = WordParserHolder()

if __name__ == '__main__':
    # cutter = WordCutter()
    # print cutter.split(u"假设你要设置的属性名为 yourProperty，属性值为 yourValue 。")
    cutter = WordParser()
    import utils

    ctrip = utils.get_docs("nlpcc_zh")
    for record in ctrip.find():
        record['words'] = cutter.split(record['text'])
        ctrip.save(record)
    print 'completed!'
