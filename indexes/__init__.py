# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import indexes.posting_index
import indexes.vocab_index
import indexes.word_text_index
import indexes.word_synonym_index
import utils.decorator


@utils.decorator.Singleton
class IndexHolder(object):
    """
    Use to select indexes from different versions & build them.
    """

    def __init__(self):
        self.posting_index = indexes.posting_index.PostingIndex()
        self.vocab_index = indexes.vocab_index.VocabIndex()
        self.word_index = indexes.word_text_index.WordTextIndex()
        # self.word_synonym_index = indexes.word_synonym_index.WordSynonymIndex()

    def build(self):
        self.posting_index.build()
        self.word_index.build()
        # self.word_synonym_index.build()
