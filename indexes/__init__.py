# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import indexes.posting_index
import indexes.vocab_index
import indexes.word_cooccurrence_index
import indexes.word_text_index
import utils.decorator


@utils.decorator.Singleton
class IndexHolder(object):
    """
    Use to select indexes from different versions & build them.
    """

    def __init__(self):
        print('just for debug: starting to init IndexHolder.')
        self.posting_index = indexes.posting_index.PostingIndex()
        self.vocab_index = indexes.vocab_index.VocabIndex()
        self.word_text_index = indexes.word_text_index.WordTextIndex()
        self.word_coocurrence_index = indexes.word_cooccurrence_index.WordCoOccurrenceIndex()
        self.init()

    def init(self, force_refresh=False):
        self.posting_index.init(force_refresh)
        self.vocab_index.init(force_refresh)
        self.word_text_index.init(force_refresh)
        self.word_coocurrence_index.init(force_refresh)
        print('-----Init index_holder successfully!')

    def build(self):
        self.posting_index.build()
        self.vocab_index.build()
        self.word_text_index.build()
        self.word_coocurrence_index.build()

