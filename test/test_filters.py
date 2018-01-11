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
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(
                text=word_text, cf=i + 1, posting={1: i + 1}))
        self.assertEqual(filters.filter_by_avgtfidf(word_text_samples, 3), word_text_samples[-1: -4: -1])

    def test_filter_by_coocurrence(self):
        word_text_samples = ['ann', 'betty', 'cindy', 'eve', 'fenn', 'tom', 'wifi', 'title']
        word_content_list = [("ann", {1: [1], 2: [1]}), ("betty", {2: [1]}), ("cindy", {1: [1], 2: [1]}),
                     ('eve', {2: [1], 3: [2]}), ('fenn', {3: [1]}), ("tom", {1: [1]}),
                     ('title', {1: [1, 0], 2: [1, 0], 3:[1, 0]}), ('wifi', {1: [1, 0], 2: [1, 0], 3:[1, 0]})]
        word_list = [entities.words.Word(text=e[0], posting=e[1]) for e in word_content_list]
        datasources.get_db().upsert_word_or_word_list(self.session, word_list)
        indexes.IndexHolder().word_coocurrence_index.init(force_refresh=True)
        ans = [('ann', 'title', 'wifi'), ('cindy', 'title', 'wifi'), ('eve', 'title', 'wifi')]
        candidates = filters.filter_by_coocurrence(
            [word_texts for word_texts in itertools.combinations(word_text_samples, 3)], 3)
        for i in range(3):
            self.assertEqual(set(ans[i]), set(candidates[i]))
