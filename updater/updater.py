# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import pyspark

import config.config_manager
import datasources.datasource
import indexes.index_holder
import spiders.spider_manager
import utils.segment

config_manager = config.config_manager.ConfigManager()
spark_config = config_manager.spark_config


class Updater(object):
    """
    use to manage crawl, create & update index/database.
    """

    def __init__(self):
        self.spider_manager = spiders.spider_manager.SpiderManager()
        self.datasource = datasources.datasource.DataSourceHolder()
        self.index_holder = indexes.index_holder.IndexHolder()
        self.text_extractor = utils.segment.TextExtractor()

    def crawl(self, num=None, numbers=None):
        self.spider_manager.crawl(num, numbers)

    def segment(self):
        sqlsession = self.datasource.create_mysql_session()
        sparksession = pyspark.sql.SparkSession(spark_config.context)
        text_df = sparksession.createDataFrame(self.datasource.find_news_plain_text(sqlsession))
        self.text_extractor.recut(text_df)

    def prepossess(self):
        self.segment()

    def update(self, num=100):
        self.crawl(num)
        self.prepossess()
