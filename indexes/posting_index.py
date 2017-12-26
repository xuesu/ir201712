# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import datasources.datasource


class PostingIndex(object):
    def __init__(self):
        self.datasource = datasources.datasource.DataSourceHolder()

    def build(self):
        pass

    def find_or(self, words_id):
        ans = dict()
        session = self.datasource.create_mysql_session()
        for word_id in words_id:
            word_posting_list = self.datasource.find_word_posting_list_by_word_id(session, word_id)
            for word_posting in word_posting_list:
                if word_posting.news_id not in ans:
                    ans[word_posting.news_id] = dict()
                ans[word_posting.news_id][word_id] = word_posting
        self.datasource.close_mysql_session(session)
        return ans
