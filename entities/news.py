# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import enum
import sqlalchemy
import sqlalchemy.orm

import entities


class NewsPlain(entities.SQLALCHEMY_BASE):
    """
    source,news_id,url,title,keywords,media_name,abstract,content,time,review_num,related_id
    e.g:
    sina,sina_comos-fynfvar5143551,http://news.sina.com.cn/s/wh/2017-10-30/doc-ifynfvar5143551.shtml,无牌宝马高速狂飙 警察截停后发现司机没有手,
    "民警,宝马,无臂",大洋网,"原标题：我伙呆！断臂“老司机”高速上驾宝马狂飙，副驾上还坐着他老婆",
    "原标题：我伙呆！断臂“老司机”高速上驾宝马狂飙，副驾上还坐着他老婆

　　一个失去双手小臂的大叔，却开着宝马带上妻子闯天涯。...",
    2017/10/30 12:28:54,0,"comos-fynfvar5052619,comos-fynhhay8321705,comos-fynfrfn0172915,comos-fynhhay8403802,comos-fynfrfn0183288"

    """
    __tablename__ = 'news_plain'

    class SourceEnum(enum.Enum):
        sina = 1
        tencent = 2
        toutiao = 3

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    source_id = sqlalchemy.Column(sqlalchemy.String(30), unique=True)
    title = sqlalchemy.Column(sqlalchemy.String(100))
    content = sqlalchemy.Column(sqlalchemy.Text)
    time = sqlalchemy.Column(sqlalchemy.DateTime)
    review_num = sqlalchemy.Column(sqlalchemy.Integer)
    abstract = sqlalchemy.Column(sqlalchemy.Text)
    keywords = sqlalchemy.Column(sqlalchemy.Text)
    source = sqlalchemy.Column(sqlalchemy.Enum(SourceEnum))
    media_name = sqlalchemy.Column(sqlalchemy.String(20))
    url = sqlalchemy.Column(sqlalchemy.String(150))
    word_num = sqlalchemy.Column(sqlalchemy.Integer)
    reviews = sqlalchemy.orm.relationship("ReviewPlain", cascade="all")
    posting_list = sqlalchemy.orm.relationship("WordPosting", back_populates="news", cascade="all")
    # The related article may not store in the db, better not to use it.
    related_id = sqlalchemy.Column(sqlalchemy.Text)

    def __repr__(self):
        return "<News Plain(source_id='{}', source='{}', abstract='{}')>".format(
            self.source_id, self.source.name, self.abstract)
