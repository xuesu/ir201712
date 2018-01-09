# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import enum
import sqlalchemy
import sqlalchemy.orm

import entities


class NewsPlain(entities.SQLALCHEMY_BASE):
    __tablename__ = 'news'

    class SourceEnum(enum.Enum):
        sina = 1
        tencent = 2
        toutiao = 3
        ifeng = 4

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    review_num = sqlalchemy.Column(sqlalchemy.Integer)
    abstract = sqlalchemy.Column(sqlalchemy.Text)
    content = sqlalchemy.Column(sqlalchemy.Text)
    keywords = sqlalchemy.Column(sqlalchemy.Text)
    title = sqlalchemy.Column(sqlalchemy.String(100))
    url = sqlalchemy.Column(sqlalchemy.String(150), unique=True)
    media_name = sqlalchemy.orm.deferred(sqlalchemy.Column(sqlalchemy.String(20)))
    source = sqlalchemy.orm.deferred(sqlalchemy.Column(sqlalchemy.Enum(SourceEnum)))
    time = sqlalchemy.Column(sqlalchemy.DateTime)
    reviews = sqlalchemy.orm.relationship("ReviewPlain", cascade="all, delete")

    def __repr__(self):
        return "<News Plain(id='{}', source='{}', abstract='{}')>".format(
            self.id, self.source.name, self.abstract)
