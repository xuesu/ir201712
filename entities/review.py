# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import enum
import sqlalchemy
import sqlalchemy.orm

import entities


class ReviewPlain(entities.SQLALCHEMY_BASE):
    """
    review_id, news_id,user_id,user_name,area,content,time,agree
    e.g:
    XXXXX, sina_comos-fynfvar5122989,3241538043,Adams_7276,江苏南京,“镜面人”大脑结构是不是也相反？,2017-10-30 11:31:05,0

    """
    __tablename__ = 'review_plain'

    class SourceEnum(enum.Enum):
        sina = 1
        tencent = 2
        toutiao = 3

    review_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news_plain.id'), nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.String(30))
    user_name = sqlalchemy.Column(sqlalchemy.String(50))
    area = sqlalchemy.Column(sqlalchemy.String(20))
    content = sqlalchemy.Column(sqlalchemy.Text)
    time = sqlalchemy.Column(sqlalchemy.DateTime)
    agree = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def __repr__(self):
        return "<Review(review_id='{}' news_id='{}', user_id='{}', time='{}')>".format(
            self.review_id, self.news_id, self.user_id, self.time)
