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

    def init(self, force_refresh=False):
        pass

    def build(self):
        pass

    def collect(self, word_texts, limit_num=1):  # there is not inexact top K collecting method.
        print('collecting posting....')
        ans = dict()
        df = dict()
        for word_text in word_texts:
            word = indexes.IndexHolder().vocab_index.collect(word_text)
            if word is None:
                continue
            for news_id in word.posting:
                if news_id not in ans:
                    ans[news_id] = dict()
                ans[news_id][word_text] = word.posting[news_id]
            df[word_text] = word.df
        limit_num = min(limit_num, len(word_texts))  # beautiful code.
        ans = {news_id: ans[news_id] for news_id in ans if len(ans[news_id]) >= limit_num}
        print('collecting posting finished')
        return ans, df
