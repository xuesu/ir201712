# -*- coding:utf-8 -*-
"""
@author: xuesu

This module is to manager configs
Example:
    port = config_manager.ConfigManager().APIconfig.port
"""

import os
import yaml

import utils.singleton

cur_dir = os.path.realpath(__file__)[:-len("config/config_manager.py")]
config_dir = os.path.join(cur_dir, "config")
logs_dir = os.path.join(cur_dir, "logs")
config_fname = os.path.join(config_dir, "config.yml")


class APIConfig(object):
    def __init__(self, config_data):
        self.app_name = config_data['app_name']
        self.port = int(config_data["port"])
        self.host = config_data["host"]
        print(self.app_name, self.port, self.host)

    def get_app_name(self):
        return self.app_name


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
