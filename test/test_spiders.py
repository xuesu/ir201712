# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import unittest

import datasources.datasource
import exceptions.base_exception
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
        session = holder.create_mysql_session()
        holder.create_mysql_all_tables()
        self.spider_manager.crawl(num=4)
        self.assertIsNotNone(holder.find_news_list(session))
        holder.drop_mysql_all_tables()