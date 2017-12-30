# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import pyspark


class SparkConfig(object):
    def __init__(self, config_data):
        self.conf = pyspark.SparkConf().setAppName(config_data['app_name']).setMaster(config_data['master'])
        self.driver_mode = True
        self.testing = True
