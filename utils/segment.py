# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import pyspark

import datasources.datasource


class TextExtractor(object):
    def __init__(self):
        self.datasource = datasources.datasource.DataSourceHolder()

    def segment(self, sparksession):
        sqlsession = self.datasource.create_mysql_session()
        text_df = sparksession.createDataFrame(self.datasource.find_news_plain_text(sqlsession))
        