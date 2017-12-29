# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import datetime
import pyspark


class Singleton(object):
    """
    Singleton is written to limit the number of instances created,
    however, it may increase time complexity due to __call__
    e.g:
        @utils.singleton.Singleton
        class A:

    """

    def __init__(self, wrapped_cls):
        self.__wrapped_cls = wrapped_cls
        self.__instance = None

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = self.__wrapped_cls(*args, **kwargs)
        return self.__instance


def run_executor_node(func):
    def wrapper(*args, **kwargs):
        import config.config_manager
        config.config_manager.ConfigManager().driver_mode = False
        return func(*args, **kwargs)

    return wrapper


def timer(func):
    def wrapper(*args, **kwargs):
        print("Starting ", func)
        start_time = datetime.datetime.now()
        ret = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        print("Ended ", func, " Spending ", (end_time - start_time).total_seconds(), "seconds")
        return ret

    return wrapper
