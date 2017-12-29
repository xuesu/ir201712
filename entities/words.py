# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import enum
import sqlalchemy
import sqlalchemy.orm

import entities


# class WordSim(entities.SQLALCHEMY_BASE):
#     wordA_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('word.id'), primary_key=True)
#     wordB_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('word.id'), primary_key=True)
#     score = sqlalchemy.Column(sqlalchemy.Float)


class WordPosting(entities.SQLALCHEMY_BASE):
    __tablename__ = 'word_posting'

    word_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('word.id'), primary_key=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news_plain.id'), primary_key=True)
    tf = sqlalchemy.Column(sqlalchemy.Integer)
    title_positions = sqlalchemy.Column(sqlalchemy.JSON)
    content_positions = sqlalchemy.Column(sqlalchemy.JSON)
    news = sqlalchemy.orm.relationship("NewsPlain", back_populates="posting_list", cascade="all, delete")
    word = sqlalchemy.orm.relationship("Word", back_populates="posting_list", cascade="all, delete")


class Word(entities.SQLALCHEMY_BASE):
    __tablename__ = 'word'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)
    pos = sqlalchemy.Column(sqlalchemy.String(5))
    df = sqlalchemy.Column(sqlalchemy.Integer)
    cf = sqlalchemy.Column(sqlalchemy.Integer)
    posting_list = sqlalchemy.orm.relationship("WordPosting", back_populates="word", cascade="all, delete")
