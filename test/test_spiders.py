# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import unittest

import datasources.datasource
import spiders.spider_manager


class SpiderManagerTest(unittest.TestCase):
    """
    Test this when net is connected.
    Yes, illegal dependence again.
    """

    def setUp(self):
        self.spider_manager = spiders.spider_manager.SpiderManager()

    def tearDown(self):
        pass

    def test_crawl(self):
        holder = datasources.datasource.DataSourceHolder(testing=True)
        holder.drop_mysql_all_tables()
        holder.create_mysql_all_tables()
        session = holder.create_mysql_session()
        self.spider_manager.crawl(num=4)
        self.assertIsNotNone(holder.find_news_list(session))
        holder.close_mysql_session(session)
        holder.drop_mysql_all_tables()
        holder.create_mysql_all_tables()
        session = holder.create_mysql_session()
        self.spider_manager.crawl(numbers=[1])
        self.assertIsNotNone(holder.find_news_list(session))
        holder.close_mysql_session(session)
        holder.drop_mysql_all_tables()
        holder.create_mysql_all_tables()
        session = holder.create_mysql_session()
        self.spider_manager.crawl(numbers={'sina': 1})
        self.assertIsNotNone(holder.find_news_list(session))
        holder.close_mysql_session(session)
        holder.drop_mysql_all_tables()