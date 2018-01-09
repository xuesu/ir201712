# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import jieba.posseg
import os

import utils.decorator

stop_nature_list = {'', 'w', 'x', 'y', 'c'}
cur_dir = os.path.realpath(__file__)[:-len("update/segment.py")]
stop_word_fname = os.path.join(cur_dir, "stop_word.txt")
with open(stop_word_fname) as fin:
    stop_word_list = set([line.strip() for line in fin.readlines()])


def is_stop_word(w):
    return w[0] in stop_word_list or w[1] in stop_nature_list


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
            word = (w, pos, start, start + width)
            if not is_stop_word(word):
                yield word
            start += width
    else:
        for w, pos in jieba.posseg.cut(unicode_sentence, HMM=HMM):  # cut for searching?
            width = len(w)
            if len(w) > 2:
                for i in range(len(w) - 1):
                    gram2 = w[i:i + 2]
                    if jieba.posseg.dt.FREQ.get(gram2):
                        word = (gram2, pos, start + i, start + i + 2)
                        if not is_stop_word(word):
                            yield word
            if len(w) > 3:
                for i in range(len(w) - 2):
                    gram3 = w[i:i + 3]
                    if jieba.posseg.dt.FREQ.get(gram3):
                        word = (gram3, pos, start + i, start + i + 3)
                        if not is_stop_word(word):
                            yield word
            word = (w, pos, start, start + width)
            if not is_stop_word(word):
                yield word
            start += width


@utils.decorator.timer
def cut4db(rdd):
    """
    
    :param rdd: a super big dataframe of news set reading from MySQL,
    in which each row is composed of (id, title, content).
    :return: 
    """

    def segment_map(r):
        """
        segment a news to 
        :param r: news entity
        :return: a list, each element is a tuple (word, dict saved its position)
        """
        words = dict()
        for word, pos_tag, position, _ in tokenize(r.title):
            if word not in words:
                words[word] = [pos_tag, r.id, 0, 0]
            words[word][-2] += 1
        for word, pos_tag, position, _ in tokenize(r.content):
            if word not in words:
                words[word] = [pos_tag, r.id, 0, 0]
            words[word][-1] += 1
        return [(k, words[k]) for k in words.keys()]

    def segment_map2(r):
        import entities.words
        word = entities.words.Word(text=r[0], df=0, cf=0, posting=dict())
        for record in r[1]:
            word.pos = record[0]
            word.cf += record[-1]
            word.df += 1
            word.posting[record[1]] = record[2:]
        return word

    return rdd.flatMap(segment_map).groupByKey().map(segment_map2).collect()
