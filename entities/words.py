# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import sqlalchemy
import sqlalchemy.orm

import entities


class WordPosting(entities.SQLALCHEMY_BASE):
    __tablename__ = 'word_posting'

    word_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('word.id'), primary_key=True, index=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news_plain.id'), primary_key=True,
                                index=True)
    tf = sqlalchemy.Column(sqlalchemy.Integer)
    content_positions = sqlalchemy.Column(sqlalchemy.JSON)
    title_positions = sqlalchemy.Column(sqlalchemy.JSON)
    news = sqlalchemy.orm.relationship("NewsPlain", back_populates="posting_list")
    word = sqlalchemy.orm.relationship("Word", back_populates="posting_list")

    def __repr__(self):
        return '<entities.words.WordPosting word_id={} news_id={} len_content={} len_title={}>'.format(
            self.word_id, self.news_id, len(self.content_positions), len(self.title_positions)
        )


class Word(entities.SQLALCHEMY_BASE):
    __tablename__ = 'word'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String(20), nullable=False, index=True)
    df = sqlalchemy.Column(sqlalchemy.Integer)
    cf = sqlalchemy.Column(sqlalchemy.Integer)
    pos = sqlalchemy.Column(sqlalchemy.String(5))
    posting_list = sqlalchemy.orm.relationship("WordPosting", back_populates="word", cascade="all, delete")
