# -*- coding:utf-8 -*-
"""
@author: xuesu
"""


class APIConfig(object):
    def __init__(self, config_data):
        self.app_name = config_data['app_name']
        self.host = config_data["host"]
        self.port = int(config_data["port"])
