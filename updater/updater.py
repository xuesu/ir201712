# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import pyspark


import config.config_manager
import datasources.datasource
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
        self.datasource_holder = datasources.datasource.DataSourceHolder()
        self.text_extractor = utils.segment.TextExtractor()

    def crawl(self, num, numbers):
        self.spider_manager.crawl(num, numbers)

    def segment(self):
        sparksession = pyspark.sql.SparkSession(spark_config.context)



