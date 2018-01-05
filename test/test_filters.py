# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""
import itertools

import datasources
import entities.news
import entities.words
import filters
import indexes
import test


class FiltersTest(test.TestCase):
    def setUp(self):
        datasources.get_db().recreate_all_tables()
        self.session = datasources.get_db().create_session()

    def tearDown(self):
        pass

    def test_filter_by_avgtfidf(self):  # TODO: to be absorb
        word_text_samples = ["1000", "10", "001", "010", "0", "1", "01"]
        for i, word_text in enumerate(word_text_samples):
            datasources.get_db().upsert_word_or_word_list(self.session,
                                                          entities.words.Word(text=word_text, df=1, cf=i + 1))
        self.assertEqual(filters.filter_by_avgtfidf(word_text_samples, 3), word_text_samples[-1: -4: -1])

    def test_filter_by_coocurrence(self):
        word_text_samples = ["abate", "bolster", "buttress", "champion", "defend", "espouse", "support"]
        for i, j in [(0, 1), (0, 2), (0, 3), (0, 2), (1, 2), (1, 3), (3, 4)]:
            datasources.get_db().upsert_news_or_news_list(
                self.session, entities.news.NewsPlain(
                    title='', content=' '.join([word_text_samples[i], word_text_samples[j]])))
        indexes.IndexHolder().word_coocurrence_index.init(force_refresh=True)
        self.assertListEqual(
            filters.filter_by_coocurrence(
                [word_texts for word_texts in itertools.combinations(word_text_samples, 3)], 3),
            [(word_text_samples[0], word_text_samples[1], word_text_samples[2]),
             (word_text_samples[0], word_text_samples[1], word_text_samples[3]),
             (word_text_samples[0], word_text_samples[2], word_text_samples[3])])
