# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import pyspark

import config
import datasources
import spiders.spider_manager
import update.segment
import utils.decorator
import indexes


@utils.decorator.Singleton
class Updater(object):
    """
    use to manage crawl, create & update index/database.
    """

    def __init__(self):
        self.sqlsession = None

    @utils.decorator.timer
    def crawl(self, num=None, numbers=None):
        spiders.spider_manager.SpiderManager().crawl(num, numbers)

    @utils.decorator.timer
    def segment(self):
        tmp = datasources.get_db().find_news_plain_text(self.sqlsession)
        partition_num = (len(tmp) + 99) // 100
        rdd = config.get_spark_context().parallelize(
            datasources.get_db().find_news_plain_text(self.sqlsession), partition_num)
        del tmp
        update.segment.cut4db(rdd)

    @utils.decorator.timer
    def prepossess(self):
        self.segment()

    @utils.decorator.timer
    def update(self, num=20):
        self.sqlsession = datasources.get_db().create_session()
        self.crawl(num)
        self.prepossess()
        datasources.get_db().close_session(self.sqlsession)
        print('wait...  we need to init IndexHolder...')
        indexes.IndexHolder().init(force_refresh=True)
        self.sqlsession = None


if __name__ == '__main__':
    updater = Updater()
    updater.update(100)
