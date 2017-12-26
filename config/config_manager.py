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

import utils.decorator

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
        self._context = None

    def _get_context(self):
        if self._context is None:
            self._context = pyspark.SparkContext(conf=self.conf)
        return self._context

    def _set_context(self, context):
        self.context = context

    context = property(_get_context, _set_context)


class FunctionsConfig(object):
    def __init__(self, config_data):
        self.suggest_num = int(config_data['suggest']['number'])


@utils.decorator.Singleton
class ConfigManager(object):
    """
    ConfigManager reads config.yml and generate config instance.
    Example:
        port = config_manager.ConfigManager().APIconfig.port
    """
    b_datasource_config = None

    def __init__(self, driver_mode=True):
        assert (os.path.isfile(config_fname)), "Couldn't find " + config_fname
        self.driver_mode = driver_mode
        with open(config_fname) as fin:
            config_data = yaml.load(fin)
            self.APIconfig = APIConfig(config_data['API'])
            self.spark_config = SparkConfig(config_data['spark'])
            self.datasource_config = DataSourceConfig(config_data['datasource'])
            self.functions_config = FunctionsConfig(config_data['functions'])
