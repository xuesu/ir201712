# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script and use a standalone schema to test.
"""

import datetime
import pandas

import datasources
import entities.news
import entities.review
import entities.words
import test


class DataSourceTest(test.TestCase):
    def setUp(self):
        """
        In fact, it is informal way to build a TestCase like this.
        :return:
        """
        datasources.get_db().recreate_all_tables()
        self.session = datasources.get_db().create_session()
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
            review_num=1)
        self.review_sample = entities.review.ReviewPlain(
            user_id=3241538043,
            user_name="Adams_7276",
            area="江苏南京",
            content="“镜面人”大脑结构是不是也相反？",
            time=datetime.datetime.strptime("2017-10-30 11:31:05", "%Y-%m-%d %H:%M:%S"),
            agree=0)
        self.news_sample.reviews = [self.review_sample]
        self.word_posting_sample = entities.words.WordPosting(tf=3,
                                                              title_positions=[1], content_positions=[1, 5])
        self.word_sample = entities.words.Word(text="江苏", pos="N", df=3, cf=3)
        self.word_sample.posting_list = [self.word_posting_sample]

    def tearDown(self):
        datasources.get_db().close_session(self.session)

    def test_find_news_list(self):
        news_list = datasources.get_db().find_news_list(self.session)
        self.assertEqual(len(news_list), 0)

    def test_upsert_news_or_news_list(self):
        """
        ugly, but simple
        :return:
        """
        datasources.get_db().upsert_news_or_news_list(self.session, self.news_sample)
        news_list = datasources.get_db().find_news_list(self.session)
        self.assertEqual(news_list[0].source_id, self.news_sample.source_id)
        self.assertIsNotNone(news_list[0].reviews[0].news_id)
        self.assertEqual(news_list[0].reviews[0].content, self.news_sample.reviews[0].content)

    def test_find_news_by_id(self):
        news = entities.news.NewsPlain()
        news = datasources.get_db().upsert_news_or_news_list(self.session, news)
        news2 = datasources.get_db().find_news_by_id(self.session, news.id)
        self.assertEqual(news.id, news2.id)

    def test_find_news_by_source_id(self):
        news = entities.news.NewsPlain(source_id="comos-fynfvar5143551")
        datasources.get_db().upsert_news_or_news_list(self.session, news)
        news2 = datasources.get_db().find_news_by_source_id(self.session, news.source_id)
        self.assertEqual(news.source_id, news2.source_id)

    def test_find_news_plain_text(self):
        datasources.get_db().upsert_news_or_news_list(self.session, self.news_sample)
        texts_df = datasources.get_db().find_news_plain_text(self.session)
        self.assertTrue(isinstance(texts_df, pandas.DataFrame))
        self.assertEqual(texts_df.shape, (1, 3))
        self.assertEqual(texts_df.title[0], self.news_sample.title)
        self.assertEqual(texts_df.content[0], self.news_sample.content)

    def test_find_word_list(self):
        word_list = datasources.get_db().find_word_list(self.session)
        self.assertEqual(len(word_list), 0)

    def test_upsert_word_or_word_list(self):
        """
        ugly, but simple
        :return:
        """
        self.news_sample = datasources.get_db().upsert_news_or_news_list(self.session, self.news_sample)
        self.word_posting_sample.news_id = self.news_sample.id
        datasources.get_db().upsert_word_or_word_list(self.session, self.word_sample)
        word_list = datasources.get_db().find_word_list(self.session)
        self.assertEqual(word_list[0].text, self.word_sample.text)
        self.assertIsNotNone(word_list[0].posting_list[0].word_id)
        self.assertListEqual(word_list[0].posting_list[0].title_positions, self.word_posting_sample.title_positions)

    def test_find_word_by_text(self):
        self.news_sample = datasources.get_db().upsert_news_or_news_list(self.session, self.news_sample)
        self.word_posting_sample.news_id = self.news_sample.id
        datasources.get_db().upsert_word_or_word_list(self.session, self.word_sample)
        word2 = datasources.get_db().find_word_by_text(self.session, self.word_sample.text)
        self.assertEqual(word2.df, self.word_sample.df)

    def test_delete_word(self):
        self.news_sample = datasources.get_db().upsert_news_or_news_list(self.session, self.news_sample)
        self.word_posting_sample.news_id = self.news_sample.id
        word2 = datasources.get_db().upsert_word_or_word_list(self.session, self.word_sample)
        datasources.get_db().delete_word(self.session, word2)
        self.assertEqual(datasources.get_db().find_word_by_text(self.session, self.word_sample.text), None)

    def test_find_word_posting_list_by_word_id(self):
        self.news_sample = datasources.get_db().upsert_news_or_news_list(self.session, self.news_sample)
        self.word_posting_sample.news_id = self.news_sample.id
        word = datasources.get_db().upsert_word_or_word_list(self.session, self.word_sample)
        word_posting_list = datasources.get_db().find_word_posting_list_by_word_id(self.session, word.id)
        self.assertEqual(word_posting_list[0].tf, self.word_posting_sample.tf)

    def test_find_word_plain_text_ordered_by_text(self):
        word_text_samples = ["1000", "10", "001", "010", "0", "1", "01"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        word_texts = datasources.get_db().find_word_plain_text_ordered_by_text(self.session)
        word_text_samples.sort()
        self.assertListEqual(word_texts, word_text_samples)
