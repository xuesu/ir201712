# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import datasources.mysql_datasource
import logs.loggers
import utils.singleton

logger = logs.loggers.LoggersHolder().get_logger("datasource")


@utils.singleton.Singleton
class DataSourceHolder(object):
    """
    Aims to balance mysql & sparksql, but contains only mysql now.
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

    def upsert_news(self, session, news):
        self.mysql_datasource.upsert_news(session, news)

    def drop_mysql_all_tables(self):
        self.mysql_datasource.drop_all_tables()

    def find_news_list(self, session, filter_by_condition=None):
        return self.mysql_datasource.find_news_list(session, filter_by_condition)

    def find_news_by_source_id(self, session, source_id):
        return self.mysql_datasource.find_news_by_source_id(session, source_id)

    def find_news_plain_text(self, session, filter_by_condition=None):
        return self.mysql_datasource.find_news_plain_text(session, filter_by_condition)
