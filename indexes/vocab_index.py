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
        if self.vocab is None:
            words = datasources.get_db().find_word_list(self.session)
            self.vocab = {word.text: word for word in words}

    @utils.decorator.timer
    def build(self):
        pass

    def collect(self, id_list):
        if self.vocab is None:
            self.init()
        if isinstance(id_list, list):
            return [self.vocab.get(text) for text in id_list]
        else:
            return self.vocab.get(id_list)
