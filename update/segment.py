# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import jieba.posseg
import os
import datasources
import utils.decorator
import config

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
            yield (w.lower(), pos, start, start + width)
            start += width
    else:
        for w, pos in jieba.posseg.cut(unicode_sentence, HMM=HMM):  # cut for searching?
            width = len(w)
            if len(w) > 2:
                for i in range(len(w) - 1):
                    gram2 = w[i:i + 2]
                    if jieba.posseg.dt.FREQ.get(gram2):
                        yield (gram2.lower(), pos, start + i, start + i + 2)
            if len(w) > 3:
                for i in range(len(w) - 2):
                    gram3 = w[i:i + 3]
                    if jieba.posseg.dt.FREQ.get(gram3):
                        yield (gram3.lower(), pos, start + i, start + i + 3)
            yield (w.lower(), pos, start, start + width)
            start += width


def tokenize_filter_stop(unicode_sentence, mode="default", HMM=True):
    for token in tokenize(unicode_sentence, mode, HMM):
        if len(token[0]) < 15 and len(token[1]) < 5 or not is_stop_word(token):
            yield token


@utils.decorator.timer
def cut4db(rdd):
    """
    
    :param rdd: a super big dataframe of news set reading from MySQL,
    in which each row is composed of (id, title, content).
    :return: 
    """

    def segment_map(r):  # (word, news_id, tf in content, tf in title if not 0)
        words = dict()
        for word, pos_tag, position, _ in tokenize_filter_stop(r.content):
            if word not in words:
                words[word] = [pos_tag, r.id, 0, 0]
            words[word][-2] += 1
        for word, pos_tag, position, _ in tokenize_filter_stop(r.title):
            if word not in words:
                words[word] = [pos_tag, r.id, 0, 0]
            words[word][-1] += 1
        return [(k, words[k] if words[k][-1] > 0 else words[k][:-1]) for k in words.keys()]

    def segment_map2(r):
        import entities.words
        word = entities.words.Word(text=r[0], cf=0, posting=dict())
        for record in r[1]:
            word.pos = record[0]
            word.posting[record[1]] = record[2:]
        word.cf = sum(sum(v) for v in word.posting.values())
        return word

    def saving_foreachPartition(words):
        import datasources
        session = datasources.get_db().create_session()
        datasources.get_db().upsert_word_or_word_list(session, [word for word in words if word.df <= 1000])
        datasources.get_db().close_session(session)

    rdd.flatMap(segment_map).groupByKey().map(segment_map2).foreachPartition(saving_foreachPartition)

