# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import sqlalchemy
import sqlalchemy.orm

import entities.review


class Word(entities.SQLALCHEMY_BASE):
    __tablename__ = 'words'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String(20), nullable=False, index=True)
    df = sqlalchemy.Column(sqlalchemy.Integer)
    cf = sqlalchemy.Column(sqlalchemy.Integer)
    pos = sqlalchemy.Column(sqlalchemy.String(5))
    posting = sqlalchemy.orm.deferred(sqlalchemy.Column(sqlalchemy.JSON, default=dict()))
