# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import os
import pyspark
import yaml

import config.API_config_manager
import config.datasource_config_manager
import config.functions_config_manager
import config.indexes_config_manager
import config.spark_config_manager

cur_dir = os.path.realpath(__file__)[:-len("config/__init__.py")]
config_dir = os.path.join(cur_dir, "config")
logs_dir = os.path.join(cur_dir, "logs")
config_fname = os.path.join(config_dir, "config.yml")

API_config = None
datasource_config = None
functions_config = None
indexes_config = None
spark_config = None
__spark_context = None
__spark_session = None


def get_spark_context():
    if config.__spark_context is None:
        config.__spark_context = pyspark.SparkContext(conf=spark_config.conf)
    return __spark_context


def get_spark_session():
    if config.__spark_session is None:
        config.__spark_session = pyspark.sql.SparkSession(config.get_spark_context())
    return __spark_session


def init():
    assert (os.path.isfile(config_fname)), "Couldn't find " + config_fname
    with open(config_fname) as fin:
        config_data = yaml.load(fin)
        config.API_config = config.API_config_manager.APIConfig(config_data['API'])
        config.datasource_config = config.datasource_config_manager.DataSourceConfig(config_data['datasource'])
        config.functions_config = config.functions_config_manager.FunctionsConfig(config_data['functions'])
        config.indexes_config = config.indexes_config_manager.IndexesConfig(config_data["indexes"])
        config.spark_config = config.spark_config_manager.SparkConfig(config_data['spark'])


init()
