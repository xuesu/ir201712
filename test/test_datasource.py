# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script and use a standalone schema to test.
"""

import datetime
import unittest

import datasources.datasource
import entities.news
import entities.review


class DataSourceTest(unittest.TestCase):
    def setUp(self):
        """
        In fact, it is informal way to build a TestCase like this.
        :return:
        """
        self.holder = datasources.datasource.DataSourceHolder(testing=True)
        self.holder.create_mysql_all_tables()
        self.session = self.holder.create_mysql_session()

    def tearDown(self):
        self.holder.close_mysql_session(self.session)
        self.holder.drop_mysql_all_tables()

    def test_find_news_list(self):
        news_list = self.holder.find_news_list(self.session)
        self.assertEqual(len(news_list), 0)

    def test_upsert_news(self):
        news = entities.news.NewsPlain(
            source=entities.news.NewsPlain.SourceEnum.sina,
            news_id="sina_comos-fynfvar5143551",
            url="http://news.sina.com.cn/s/wh/2017-10-30/doc-ifynfvar5143551.shtml",
            title="无牌宝马高速狂飙 警察截停后发现司机没有手",
            keywords="民警,宝马,无臂",
            media_name="大洋网",
            abstract="原标题：我伙呆！断臂“老司机”高速上驾宝马狂飙，副驾上还坐着他老婆",
            content="原标题：我伙呆！断臂“老司机”高速上驾宝马狂飙，副驾上还坐着他老婆\n一个失去双手小臂的大叔，却开着宝马带上妻子闯天涯。...",
            time=datetime.datetime.strptime("2017/10/30 12:28:54", "%Y/%m/%d %H:%M:%S"),
            review_num=0)
        news.reviews = [entities.review.ReviewPlain(
            review_id="XXXXX",
            news_id="sina_comos-fynfvar5143551",
            user_id=3241538043,
            user_name="Adams_7276",
            area="江苏南京",
            content="“镜面人”大脑结构是不是也相反？",
            time=datetime.datetime.strptime("2017-10-30 11:31:05", "%Y-%m-%d %H:%M:%S"),
            agree=0)]
        self.holder.upsert_news(self.session, news)
        news_list = self.holder.find_news_list(self.session)
        self.assertEqual(news_list[0].news_id, news.news_id)
        self.assertEqual(news_list[0].reviews[0].review_id, news.reviews[0].review_id)

    def test_find_news_by_id(self):
        news = entities.news.NewsPlain(news_id="sina_comos-fynfvar5143551")
        self.holder.upsert_news(self.session, news)
        news2 = self.holder.find_news_by_id(self.session, news.news_id)
        self.assertEqual(news.news_id, news2.news_id)
