# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import datasources
import utils.decorator


class VocabIndex(object):
    def __init__(self):
        self.vocab = None

    def init(self, force_refresh=False):
        session = datasources.get_db().create_session()
        words = datasources.get_db().find_word_list(session)
        print('typeof words', type(words))
        self.vocab = {word.text: word for word in words}

    @utils.decorator.timer
    def build(self):
        pass

    def collect(self, text_list):
        if self.vocab is None:
            self.init()
        if isinstance(text_list, list) or isinstance(text_list, set):
            return [self.vocab.get(text) for text in text_list if text in self.vocab]
        else:
            return self.vocab.get(text_list)
