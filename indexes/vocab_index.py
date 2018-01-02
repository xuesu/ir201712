# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import datasources
import utils.decorator


class VocabIndex(object):
    def __init__(self):
        self.vocab = None
        # ORM session, plz keep it.
        # but try to limit the access of deferred columns
        self.session = datasources.get_db().create_session()

    def __del__(self):
        datasources.get_db().close_session(self.session)

    def init(self, force_refresh=False):
        words = datasources.get_db().find_word_list(self.session)
        self.vocab = {word.text: word for word in words}

    @utils.decorator.timer
    def build(self):
        pass

    def collect(self, text_list):
        if isinstance(text_list, str):
            return self.vocab.get(text_list)
        else:
            return [self.vocab.get(text) for text in text_list]
