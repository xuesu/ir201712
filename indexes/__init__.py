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

        self.posting_index = indexes.posting_index.PostingIndex()
        self.vocab_index = indexes.vocab_index.VocabIndex()
        self.word_text_index = indexes.word_text_index.WordTextIndex()
        self.word_coocurrence_index = indexes.word_cooccurrence_index.WordCoOccurrenceIndex()
        print('starting to initial...')
        self.init()

    @utils.decorator.timer
    def init(self, force_refresh=False):
        print('starting to initial...  in init()')
        self.posting_index.init(force_refresh)
        self.vocab_index.init(force_refresh)
        self.word_text_index.init(force_refresh)
        self.word_coocurrence_index.init(force_refresh)
        print('inited.')

    def build(self):
        self.posting_index.build()
        self.vocab_index.build()
        self.word_text_index.build()
        self.word_coocurrence_index.build()

