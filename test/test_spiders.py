# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import datasources
import spiders.spider_manager
import test


class SpiderManagerTest(test.TestCase):
    """
    Test this when net is connected.
    Yes, illegal dependence again.
    """

    def setUp(self):
        datasources.get_db().recreate_all_tables()
        self.spider_manager = spiders.spider_manager.SpiderManager()

    def tearDown(self):
        pass

    def test_crawl(self):  # TODO: how to update indexes meanwhile crawling
        db = datasources.get_db()
        session = db.create_session()
        self.spider_manager.crawl(num=16)
        self.assertIs(len(db.find_news_list(session)), 16)
