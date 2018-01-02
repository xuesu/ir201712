# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""
import datasources
import entities.news
import entities.review
import functions.emotions
import test


class EmotionsTest(test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_analyze_emotion4news(self):
        review_texts = ["真不错", "", "真差", "ABCDSFDSFADFA", '1' * 500]
        reviews = [entities.review.ReviewPlain(content=text) for text in review_texts]
        news_sample = entities.news.NewsPlain(reviews=reviews)
        session = datasources.get_db().create_session()
        news_sample = datasources.get_db().upsert_news_or_news_list(session, news_sample)
        self.assertEqual(len(functions.emotions.analyze_emotion4news(session, news_sample.id)), 5)
        datasources.get_db().close_session(session)
