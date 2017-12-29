# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import datasources.mysql_datasource
import logs.loggers
import utils.decorator

logger = logs.loggers.LoggersHolder().get_logger("datasource")


@utils.decorator.Singleton
class DataSourceHolder(object):
    """
    Aims to balance mysql & sparksql, but contains only mysql now.
    Datasource involved are all singletons, so pls do not put any thread-unsafe variable in it.
    """

    def __init__(self, testing=False):
        self.mysql_datasource = datasources.mysql_datasource.MySQLDataSource(testing)

    def connect(self):
        self.mysql_datasource.connect()

    def create_mysql_session(self):
        return self.mysql_datasource.create_session()

    def close_mysql_session(self, session):
        self.mysql_datasource.close_session(session)

    def create_mysql_all_tables(self):
        self.mysql_datasource.create_all_tables()

    def drop_mysql_all_tables(self):
        self.mysql_datasource.drop_all_tables()

    def upsert_news(self, session, news):
        return self.mysql_datasource.upsert_news(session, news)

    def find_news_list(self, session, filter_by_condition=None, order_by_condition=None):
        return self.mysql_datasource.find_news_list(session, filter_by_condition, order_by_condition)

    def find_news_by_source_id(self, session, source_id):
        return self.mysql_datasource.find_news_by_source_id(session, source_id)

    def find_news_plain_text(self, session, filter_by_condition=None):
        return self.mysql_datasource.find_news_plain_text(session, filter_by_condition)

    def upsert_word(self, session, word):
        return self.mysql_datasource.upsert_word(session, word)

    def find_word_list(self, session, filter_by_condition=None, order_by_condition=None):
        return self.mysql_datasource.find_word_list(session, filter_by_condition, order_by_condition)

    def find_word_by_text(self, session, text):
        return self.mysql_datasource.find_word_by_text(session, text)

    def delete_word(self, session, word):
        self.mysql_datasource.delete_word(session, word)

    def find_word_posting_list(self, session, filter_by_condition=None):
        return self.mysql_datasource.find_word_posting_list(session, filter_by_condition)

    def find_word_posting_list_by_word_id(self, session, word_id):
        return self.mysql_datasource.find_word_posting_list_by_word_id(session, word_id)
