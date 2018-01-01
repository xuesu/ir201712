# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import copy
import enum

import config
import datasources
import exceptions.indexes_exceptions
import utils.decorator
import utils.utils


class Node(object):
    def __init__(self):
        self.children = dict()
        self.leaf = False

    def __del__(self):
        for child in self.children:
            del child

    def step(self, s):
        node = self
        ind = 0
        for c in s:
            nxt_node = node.children.get(c, None)
            if nxt_node is None:
                return ind, node
            node = nxt_node
            ind += 1
        return ind, node

    def collect_prefix(self, s='', prefixes=None):
        if prefixes is None:
            prefixes = ['']
        ans = []
        if s and s[0] != '*':
            if s[0] not in self.children.keys():
                return []
            valid_c = [s[0]]
        else:
            valid_c = self.children.keys()
        for c in valid_c:
            new_prefixes = [prefix + c for prefix in prefixes]
            ans += self.children[c].collect_prefix(s[1:] if len(s) > 1 else '', new_prefixes)
        if self.leaf and ((not s) or s == '*' * len(s)):
            return ans + prefixes
        else:
            return ans

    def add_tostr(self):
        tmp = ['{}'.format(self.leaf)]
        for c in self.children:
            tmp.append('%c: {%s}' % (c, self.children[c].add_tostr()))
        return ','.join(tmp)

    def add_replace_or_register(self, register):
        for c in self.children:
            child = self.children[c]
            if len(child.children.keys()) > 0:
                child.add_replace_or_register(register)
                child_str = child.add_tostr()
                if child_str in register:
                    self.children[c] = register[child_str]
                    del child
                else:
                    register[child_str] = child

    def add(self, s, register):
        ind, node = self.step(s)
        if len(node.children.keys()) > 0:
            node.add_replace_or_register(register)
        for c in s[ind:]:
            node.children[c] = Node()
            node = node.children[c]
        node.leaf = True

    def collect_similar(self, pattern, rthreshold, prefixes=None):
        if rthreshold < 0:
            raise exceptions.indexes_exceptions.WordTextSimilarInvalidEditorDistanceThreshold(pattern, self)
        penalties = config.indexes_config.word_text_similar_penalties
        if prefixes is None:
            prefixes = {""}
        if not pattern and self.leaf:
            ans = {prefix: rthreshold for prefix in prefixes}
        else:
            ans = dict()
        for c in self.children:
            new_prefixes = {prefix + c for prefix in prefixes}
            if pattern and (pattern[0] == '*' or pattern[0] == c):
                cans = self.children[c].collect_similar(pattern[1:], rthreshold, new_prefixes)
                ans = utils.utils.merge_dict_using_bigger_v(ans, cans)
            if rthreshold >= penalties[1]:
                cans = self.children[c].collect_similar(pattern, rthreshold - penalties[1], new_prefixes)
                ans = utils.utils.merge_dict_using_bigger_v(ans, cans)
            if pattern and rthreshold >= penalties[2]:
                cans = self.children[c].collect_similar(pattern[1:], rthreshold - penalties[2], new_prefixes)
                ans = utils.utils.merge_dict_using_bigger_v(ans, cans)

        if pattern and rthreshold >= penalties[0]:
            cans = self.collect_similar(pattern[1:], rthreshold - penalties[0], prefixes)
            ans = utils.utils.merge_dict_using_bigger_v(ans, cans)
        return ans


class WordTextIndex(object):
    """
    A temporary solution using Minimal Acyclic Finite State Automata
    """

    def __init__(self):
        self.tree = None

    class CollectionAction(enum.Enum):
        PREFIX = 0
        SIMILAR = 1

    def init(self, force_refresh=False):
        self.build()

    @utils.decorator.timer
    def build(self):
        session = datasources.get_db().create_session()
        word_texts = datasources.get_db().find_word_plain_text_ordered_by_text(session)
        datasources.get_db().close_session(session)
        self.tree = Node()
        register = dict()
        for word_text in word_texts:
            self.tree.add(word_text, register)
        del register

    @utils.decorator.timer
    def collect(self, s='', action=CollectionAction.PREFIX, threshold=None):
        if action == WordTextIndex.CollectionAction.PREFIX:
            return self.tree.collect_prefix(s)
        else:
            if threshold is None:
                threshold = config.indexes_config.word_text_similar_default_threshold
            text2score = self.tree.collect_similar(s, threshold)
            text2score = [(text2score[text], text) for text in text2score]
            text2score.sort(reverse=True)
            return [st[1] for st in text2score]
