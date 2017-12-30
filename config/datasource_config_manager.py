# -*- coding:utf-8 -*-
"""
@author: xuesu
"""


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
