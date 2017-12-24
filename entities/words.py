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

    class FieldEnum(enum.Enum):
        title = 1
        content = 2

    word_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('word.id'), primary_key=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news_plain.id'), primary_key=True)
    tf = sqlalchemy.Column(sqlalchemy.Integer)
    positions = sqlalchemy.Column(sqlalchemy.JSON)
    field_id = sqlalchemy.Column(sqlalchemy.Enum(FieldEnum))


class Word(entities.SQLALCHEMY_BASE):
    __tablename__ = 'word'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    text = sqlalchemy.Column(sqlalchemy.String(20), unique=True, nullable=False)
    pos = sqlalchemy.Column(sqlalchemy.String(5))
    df = sqlalchemy.Column(sqlalchemy.Integer)
    posting_lists = sqlalchemy.orm.relationship("WordPosting", cascade="all")
