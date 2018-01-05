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
        db.recreate_all_tables()
        session = db.create_session()
        self.spider_manager.crawl(num=4)
        self.assertIsNotNone(db.find_news_list(session))
        db.recreate_all_tables()
