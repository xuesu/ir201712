# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import enum


import datasources
import utils.decorator


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

    def collect(self, s='', prefixs=None):
        if prefixs is None:
            prefixs = ['']
        ans = []
        if s and s[0] != '*':
            if s[0] not in self.children.keys():
                return []
            valid_c = [s[0]]
        else:
            valid_c = self.children.keys()
        for c in valid_c:
            new_prefixs = [prefix + c for prefix in prefixs]
            ans += self.children[c].collect(s[1:] if len(s) > 1 else '', new_prefixs)
        if self.leaf and ((not s) or s == '*' * len(s)):
            return ans + prefixs
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


class WordTextIndex(object):
    """
    A temporary solution using Minimal Acyclic Finite State Automata
    """

    def __init__(self):
        self.tree = None

    class CollectionAction(enum.Enum):
        PREFIX = 0
        SIMILAR = 1

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
    def collect(self, s='', spell_mode=CollectionAction.PREFIX):
        if spell_mode == WordTextIndex.CollectionAction.PREFIX:
            return self.tree.collect(s)
        else:
            return None
