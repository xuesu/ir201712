# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import os
import pyspark
import sys


class SparkConfig(object):
    def __init__(self, config_data):
        self.pythonseed = config_data["spark.executorEnv.PYTHONHASHSEED"]
        self.executor_memory = config_data['spark.executor.memory']
        os.environ["PYTHONHASHSEED"] = str(self.pythonseed)
        pt = [pt for pt in sys.path if 'python' in pt and pt.endswith('site-packages')][0]
        python_path = os.path.join(pt[:pt.rfind('/lib/')], 'bin', 'python')
        os.environ["PYSPARK_PYTHON"] = python_path
        os.environ["PYSPARK_DRIVER_PYTHON"] = python_path
        self.conf = pyspark.SparkConf().setAppName(config_data['app_name']).\
            setMaster(config_data['master']).set("spark.executorEnv.PYTHONHASHSEED", self.pythonseed)\
            .set("spark.executor.memory", self.executor_memory)
        self.conf = self.conf
        self.driver_mode = True
        self.testing = False
