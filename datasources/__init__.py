# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import config
import datasources.mysql_datasource

__db = None


def get_db():
    if datasources.__db is None:
        datasources.__db = datasources.mysql_datasource.MySQLDataSource(testing=config.spark_config.testing)
    return datasources.__db


def set_db(db):
    datasources.__db = db
