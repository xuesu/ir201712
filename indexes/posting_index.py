# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import enum

import indexes
import utils.decorator


class PostingIndex(object):
    def __init__(self):
        self.inited = True

    class LogicAction(enum.Enum):
        OR = 0
        AND = 1

    def init(self, force_refresh=False):
        pass

    def build(self):
        pass

    def collect(self, word_texts, action=LogicAction.OR):  # there is not inexact top K collecting method.
        ans = dict()
        for word_text in word_texts:
            word_posting = indexes.IndexHolder().vocab_index.collect(word_text).posting
            for news_id in word_posting:
                if news_id not in ans:
                    ans[news_id] = dict()
                ans[news_id][word_text] = word_posting[news_id]
        if action == PostingIndex.LogicAction.AND:
            ans = {news_id: ans[news_id] for news_id in ans if len(ans[news_id]) == len(word_texts)}
        return ans
