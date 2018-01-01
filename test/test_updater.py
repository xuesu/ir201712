# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import datasources.mysql_datasource
import test
import update


class UpdaterTest(test.TestCase):
    """
    Test this when net is connected.
    Yes, illegal dependence again.
    """

    def setUp(self):
        datasources.get_db().recreate_all_tables()
        self.updater = update.Updater()

    def tearDown(self):
        pass

    def test_update(self):
        self.updater.update(20)
        session = datasources.get_db().create_session()
        self.assertIsNotNone(datasources.get_db().find_news_list(session))
        self.assertIsNotNone(datasources.get_db().find_word_list(session))
        datasources.get_db().close_session(session)
