# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import indexes.posting_index
import indexes.word_index
import utils.decorator


@utils.decorator.Singleton
class IndexHolder(object):
    """
    Use to select indexes from different versions & build them.
    """

    def __init__(self):
        self.posting_index = indexes.posting_index.PostingIndex()
        self.word_index = indexes.word_index.WordIndex()

    def build(self):
        self.posting_index.build()
        self.word_index.build()

    def get_posting_index(self):
        return self.posting_index

    def get_word_index(self):
        return self.word_index
