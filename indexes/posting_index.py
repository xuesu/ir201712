# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import enum


import datasources
import utils.decorator


class PostingIndex(object):
    def __init__(self):
        # ORM session, plz keep it.
        self.session = datasources.get_db().create_session()
        self.inited = True

    def __del__(self):
        datasources.get_db().close_session(self.session)

    class LogicAction(enum.Enum):
        OR = 0
        AND = 1

    def init(self, force_refresh=False):
        pass

    def build(self):
        pass

    @utils.decorator.timer
    def collect(self, word_ids, action=LogicAction.OR):  # there is not inexact top K collecting method.
        ans = dict()
        for word_id in word_ids:
            word_posting_list = datasources.get_db().find_word_posting_list_by_word_id(self.session, word_id)
            for word_posting in word_posting_list:
                if word_posting.news_id not in ans:
                    ans[word_posting.news_id] = dict()
                ans[word_posting.news_id][word_id] = word_posting
        if action == PostingIndex.LogicAction.AND:
            ans = {news_id: ans[news_id] for news_id in ans if len(ans[news_id]) == len(word_ids)}
        return ans
