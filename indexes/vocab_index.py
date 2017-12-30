# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import datasources
import utils.decorator


class VocabIndex(object):
    """
    A temporary solution using Minimal Acyclic Finite State Automata
    """

    def __init__(self):
        self.vocab = None
        # ORM session, plz keep it.
        self.session = datasources.get_db().create_session()

    def __del__(self):
        datasources.get_db().close_session(self.session)

    @utils.decorator.timer
    def build(self):
        words = datasources.get_db().find_word_list(self.session)
        self.vocab = {word.text: word for word in words}

    def collect(self, text):
        return self.vocab.get(text, None)
