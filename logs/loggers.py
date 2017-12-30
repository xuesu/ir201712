# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import os
import logging
import logging.config
import logging.handlers

import config
import utils.decorator


@utils.decorator.Singleton
class LoggersHolder(object):
    """
    This class is actually nonsense, just to prevent multiple logger settings overlap.
    But it is actually useless.
    """

    def __init__(self):
        self.loggers = dict()

    def get_logger(self, name, level='INFO'):
        if name not in self.loggers:
            self.new_logger(name, level)
        self.loggers[name].setLevel(level)
        return self.loggers[name]

    def new_logger(self, name, level):
        logger = logging.getLogger(name)
        stream_handler = logging.StreamHandler()
        file_handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(config.logs_dir, "{}.log".format(name)), when='D')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m-%d %H:%M:%S')
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        file_handler.setLevel('INFO')
        logger.setLevel(level)
        self.loggers[name] = logger


logging.getLogger('py4j').setLevel(logging.WARN)
