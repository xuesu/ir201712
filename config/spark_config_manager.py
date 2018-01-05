# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import os
import pyspark


class SparkConfig(object):
    def __init__(self, config_data):
        self.pythonseed = config_data["spark.executorEnv.PYTHONHASHSEED"]
        os.environ["PYTHONHASHSEED"] = str(self.pythonseed)
        os.environ["PYSPARK_PYTHON"] = "/home/airplus/installation/miniconda3/envs/env_name/bin/python3.6"
        os.environ["PYSPARK_DRIVER_PYTHON"] = "/home/airplus/installation/miniconda3/envs/env_name/bin/python3.6"
        self.conf = pyspark.SparkConf().setAppName(config_data['app_name']).\
            setMaster(config_data['master']).set("spark.executorEnv.PYTHONHASHSEED", self.pythonseed)
        self.conf = self.conf
        self.driver_mode = True
        self.testing = False
