# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import math


def sort_by_avgtfidf(words, keep_num):
    words_graded = [((word.cf + 2) / math.log(word.df + 2), word) for word in words]
    words_graded.sort(reverse=True)
    return [word_grade[1] for word_grade in words_graded][:keep_num]


def sort_by_bm25():
    pass
