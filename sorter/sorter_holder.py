# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import sorter.word_suggest_sorter
import sorter.bm25_sorter
import utils.decorator


@utils.decorator.Singleton
class SorterHolder(object):
    """
    Use to select indexes from different versions & build them.
    """

    def __init__(self):
        self.word_suggest_sorter = sorter.word_suggest_sorter.Word_Suggest_Sorter()

