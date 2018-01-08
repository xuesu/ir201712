# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import config
import datasources.mysql_datasource
import datasources.redis_datasource

__db = None
__redis = None


def get_db():
    if datasources.__db is None:
        datasources.__db = datasources.mysql_datasource.MySQLDataSource(testing=config.spark_config.testing)
    return datasources.__db


def set_db(db):
    datasources.__db = db


def get_redis():
    if datasources.__redis is None:
        datasources.__redis = datasources.redis_datasource.RedisDataSource()
    return datasources.__redis


def set_redis():
    datasources.__redis = __redis
