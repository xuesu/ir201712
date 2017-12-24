# -*- coding:utf-8 -*-
"""
@author: xuesu

This module is to manager configs
Example:
    port = config_manager.ConfigManager().APIconfig.port
"""

import os
import pyspark
import yaml

import utils.singleton

cur_dir = os.path.realpath(__file__)[:-len("config/config_manager.py")]
config_dir = os.path.join(cur_dir, "config")
logs_dir = os.path.join(cur_dir, "logs")
config_fname = os.path.join(config_dir, "config.yml")


class APIConfig(object):
    def __init__(self, config_data):
        self.app_name = config_data['app_name']
        self.host = config_data["host"]
        self.port = int(config_data["port"])

    def get_app_name(self):
        return self.app_name


class DataSourceConfig(object):
    def __init__(self, config_data):
        self.host = config_data["host"]
        self.port = int(config_data["port"])
        self.user = config_data['user']
        self.password = config_data['password']
        self.database_name = config_data['database_name']
        self.test_database_name = config_data['test_database_name']
        self.pool_size = int(config_data['pool_size'])
        self.max_overflow = int(config_data['max_overflow'])
        self.timeout = int(config_data['timeout'])
        self.rebuild = config_data['rebuild']


class SparkConfig(object):
    def __init__(self, config_data):
        self.conf = pyspark.SparkConf().setAppName(config_data['app_name']).setMaster(config_data['master'])
        self.context = pyspark.SparkContext(conf=self.conf)


@utils.singleton.Singleton
class ConfigManager(object):
    """
    ConfigManager reads config.yml and generate config instance.
    Example:
        port = config_manager.ConfigManager().APIconfig.port
    """

    def __init__(self):
        assert (os.path.isfile(config_fname)), "Couldn't find " + config_fname
        with open(config_fname) as fin:
            config_data = yaml.load(fin)
            self.APIconfig = APIConfig(config_data['API'])
            self.datasource_config = DataSourceConfig(config_data['datasource'])
            self.spark_config = SparkConfig(config_data['spark'])
