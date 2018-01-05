# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import math
import random

import indexes


def filter_by_avgtfidf(word_texts, keep_num):
    if len(word_texts) <= keep_num:
        return word_texts
    words = indexes.IndexHolder().vocab_index.collect(word_texts)  # TODO: to be absorb, what is this
    words_graded = [((word.cf + 2) / math.log(word.df + 2), word) for word in words if word is not None]
    words_graded.sort(reverse=True, key=lambda x: x[0])

    words_graded = [word_grade[1].text for word_grade in words_graded]
    return words_graded[:keep_num]


def filter_by_coocurrence(word_texts_list, keep_num):
    if len(word_texts_list) <= keep_num:
        return word_texts_list
    words_texts_graded_list = [(indexes.IndexHolder().word_coocurrence_index.collect(word_texts), word_texts)
                               for word_texts in word_texts_list]
    words_texts_graded_list.sort(reverse=True, key=lambda x: x[0])
    words_texts_graded_list = [word_texts_grade[1] for word_texts_grade in words_texts_graded_list]
    return words_texts_graded_list[:keep_num]


def filter_by_word_length_then_random(word_texts, keep_num):
    if len(word_texts) <= keep_num:
        return word_texts
    random.shuffle(word_texts)
    word_texts.sort(reverse=True, key=len)
    return word_texts[:keep_num]


def filter_by_random(word_texts, keep_num):
    if len(word_texts) <= keep_num:
        return word_texts
    return random.sample(word_texts, keep_num)
