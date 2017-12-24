# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script and use a standalone schema to test.
"""

import datetime
import pandas
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
        self.news_sample = entities.news.NewsPlain(
            source=entities.news.NewsPlain.SourceEnum.sina,
            source_id="comos-fynfvar5143551",
            url="http://news.sina.com.cn/s/wh/2017-10-30/doc-ifynfvar5143551.shtml",
            title="无牌宝马高速狂飙 警察截停后发现司机没有手",
            keywords="民警,宝马,无臂",
            media_name="大洋网",
            abstract="原标题：我伙呆！断臂“老司机”高速上驾宝马狂飙，副驾上还坐着他老婆",
            content="原标题：我伙呆！断臂“老司机”高速上驾宝马狂飙，副驾上还坐着他老婆\n一个失去双手小臂的大叔，却开着宝马带上妻子闯天涯。...",
            time=datetime.datetime.strptime("2017/10/30 12:28:54", "%Y/%m/%d %H:%M:%S"),
            review_num=0)
        self.review_sample = entities.review.ReviewPlain(
            user_id=3241538043,
            user_name="Adams_7276",
            area="江苏南京",
            content="“镜面人”大脑结构是不是也相反？",
            time=datetime.datetime.strptime("2017-10-30 11:31:05", "%Y-%m-%d %H:%M:%S"),
            agree=0)
        self.news_sample.reviews = [self.review_sample]

    def tearDown(self):
        self.holder.close_mysql_session(self.session)
        self.holder.drop_mysql_all_tables()

    def test_find_news_list(self):
        news_list = self.holder.find_news_list(self.session)
        self.assertEqual(len(news_list), 0)

    def test_upsert_news(self):
        self.holder.upsert_news(self.session, self.news_sample)
        news_list = self.holder.find_news_list(self.session)
        self.assertEqual(news_list[0].source_id, self.news_sample.source_id)
        self.assertIsNotNone(news_list[0].reviews[0].news_id)
        self.assertEqual(news_list[0].reviews[0].content, self.news_sample.reviews[0].content)

    def test_find_news_by_source_id(self):
        news = entities.news.NewsPlain(source_id="comos-fynfvar5143551")
        self.holder.upsert_news(self.session, news)
        news2 = self.holder.find_news_by_source_id(self.session, news.source_id)
        self.assertEqual(news.source_id, news2.source_id)

    def test_find_news_plain_text(self):
        self.holder.upsert_news(self.session, self.news_sample)
        texts_df = self.holder.find_news_plain_text(self.session)
        self.assertTrue(isinstance(texts_df, pandas.DataFrame))
        self.assertEqual(texts_df.shape, (1, 3))
        self.assertEqual(texts_df.title[0], self.news_sample.title)
        self.assertEqual(texts_df.content[0], self.news_sample.content)
