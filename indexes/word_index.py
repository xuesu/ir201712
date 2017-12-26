# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import datasources.datasource


class RegisterTreeNode(object):
    def __init__(self):
        self.children = dict()
        self.eqnode = None

    def __del__(self):
        self.stop()

    def step(self, s):
        node = self
        ind = len(s)
        for c in s[-1: -len(s): -1]:
            nxt_node = node.children.get(c, None)
            if nxt_node is None:
                return ind, node
            node = nxt_node
            ind -= 1
        return ind, node

    def stop(self):
        for child in self.children:
            del child


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

    def add(self, s, register):
        ind, node = self.step(s)
        ind2, node2 = register.step(s[ind + 1:])
        ind2 += ind + 1
        new_nodes = []
        for c in s[ind: ind2 - 1]:
            node.children[c] = Node()
            node = node.children[c]
            new_nodes.append(node)
        if ind2 != len(s):
            node.children[s[ind2 - 1]] = node2.eqnode
        else:
            node.children[s[-1]] = Node()
            node.children[s[-1]].leaf = True
        for i, c in enumerate(s[-1 - ind:- ind2: -1]):
            node2.children[c] = RegisterTreeNode()
            node2 = node2.children[c]
            node2.eqnode = new_nodes[-1 - i]
        del new_nodes


class WordIndex(object):
    """
    A temporary solution using Minimal Acyclic Finite State Automata
    """

    def __init__(self):
        self.datasource = datasources.datasource.DataSourceHolder()
        self.tree = None
        self.vocab = None

    def build(self):
        session = self.datasource.create_mysql_session()
        words = self.datasource.find_word_list(session, order_by_condition="text")
        self.datasource.close_mysql_session(session)
        self.tree = Node()
        register = RegisterTreeNode()
        for word in words:
            self.tree.add(word.text, register)
        del register
        self.vocab = {word.text: word for word in words}

    def collect(self, s=''):
        return [self.vocab[word_text] for word_text in self.tree.collect(s)]


index = WordIndex()
index.build()
index.collect()