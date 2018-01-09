# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import sqlalchemy
import sqlalchemy.orm

import entities


class ReviewPlain(entities.SQLALCHEMY_BASE):
    __tablename__ = 'reviews'
    review_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news.id'), nullable=False)
    agree = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    content = sqlalchemy.Column(sqlalchemy.Text)
    time = sqlalchemy.orm.deferred(sqlalchemy.Column(sqlalchemy.DateTime))
    user_id = sqlalchemy.orm.deferred(sqlalchemy.Column(sqlalchemy.String(30)))
    user_name = sqlalchemy.orm.deferred(sqlalchemy.Column(sqlalchemy.String(50)))

    def __repr__(self):
        return "<Review(review_id='{}' news_id='{}', user_id='{}')>".format(
            self.review_id, self.news_id, self.user_id)
