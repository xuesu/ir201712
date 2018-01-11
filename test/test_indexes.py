# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import datasources
import entities.news
import entities.words
import indexes.posting_index
import indexes.vocab_index
import indexes.word_cooccurrence_index
import indexes.word_text_index
import test


class IndexesTest(test.TestCase):
    def setUp(self):
        datasources.get_db().recreate_all_tables()
        self.session = datasources.get_db().create_session()

    def tearDown(self):
        pass

    def test_vocab_index(self):
        word_text_samples = ["1000", "10", "001", "010", "0", "1", "01"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        index = indexes.vocab_index.VocabIndex()
        index.init()
        self.assertIsNotNone(index.collect("1"))
        self.assertEqual(len(index.collect("1").posting), 0)
        self.assertIsNone(index.collect("a"))

    def test_word_text_index(self):
        word_text_samples = ["野猫", "野小猫", "野生小猫", "猫", "野狗", "豹猫", "小野猫",
                             "1000", "10", "001", "010", "0", "1", "01", "1001"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        index = indexes.word_text_index.WordTextIndex()
        index.init(force_refresh=True)
        word_texts = index.collect()
        word_texts.sort()
        word_text_samples.sort()
        self.assertListEqual(word_texts, word_text_samples)

    def test_word_text_index_prefix(self):
        word_text_samples = ["1000", "10", "001", "010", "0", "1", "01"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        index = indexes.word_text_index.WordTextIndex()
        index.init(force_refresh=True)
        word_texts = index.collect('', action=index.CollectionAction.PREFIX)
        word_texts.sort()
        word_text_samples.sort()
        self.assertListEqual(word_texts, word_text_samples)

    def test_word_text_index_similar(self):
        word_text_samples = ["野猫", "野小猫", "野生小猫", "猫", "野狗", "豹猫", "小野猫",
                             "1000", "10", "001", "010", "0", "1", "01"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        index = indexes.word_text_index.WordTextIndex()
        index.init(force_refresh=True)
        word_texts = index.collect("野猫", action=index.CollectionAction.SIMILAR, threshold=1)
        word_texts.sort()
        word_text_ans = ["野猫", "野小猫", "猫", "野狗", "豹猫", "小野猫"]
        word_text_ans.sort()
        self.assertListEqual(word_texts, word_text_ans)
        word_texts = index.collect("猫", action=index.CollectionAction.SIMILAR, threshold=2)
        word_texts.sort()
        word_text_ans = ["0", "1", "猫", "01", "10", "野猫", "豹猫", "野狗", "小野猫", "野小猫"]
        word_text_ans.sort()
        self.assertListEqual(word_texts, word_text_ans)

    def test_word_text_index_samelength(self):
        word_text_samples = ["野猫", "野小猫", "野生小猫", "猫", "野狗", "豹猫", "小野猫",
                             "1000", "10", "001", "010", "0", "1", "01"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        index = indexes.word_text_index.WordTextIndex()
        index.init(force_refresh=True)
        word_texts = index.collect("野*", action=index.CollectionAction.SAMELENGTH)
        word_texts.sort()
        word_text_ans = ["野猫", "野狗"]
        word_text_ans.sort()
        self.assertListEqual(word_texts, word_text_ans)

    def test_posting_index(self):
        words_list = [entities.words.Word(text="a"), entities.words.Word(text="b")]
        words_list[0].posting = {1: [2, 3], 3: [0, 1]}
        words_list[1].posting = {1: [1, 1]}
        datasources.get_db().upsert_word_or_word_list(self.session, words_list)
        index = indexes.posting_index.PostingIndex()
        index.init(force_refresh=True)
        self.assertEqual(len(index.collect(['a', 'b'], 1)), 2)
        self.assertEqual(len(index.collect(['a', 'b'], 2)), 1)

    def test_word_cooccurrence_index(self):
        word_content_list = [("ann", {1: [1], 2: [1]}), ("betty", {2: [1]}), ("cindy", {1: [1], 2: [1]}),
                     ('eve', {2: [1], 3: [2]}), ('fenn', {3: [1]}), ("tom", {1: [1]}),
                     ('title', {1: [1, 0], 2: [1, 0], 3:[1, 0]}), ('wifi', {1: [1, 0], 2: [1, 0], 3:[1, 0]})]
        word_list = [entities.words.Word(text=e[0], posting=e[1]) for e in word_content_list]
        datasources.get_db().upsert_word_or_word_list(self.session, word_list)
        index = indexes.word_cooccurrence_index.WordCoOccurrenceIndex()
        index.init(force_refresh=True)
        self.assertEqual(index.collect(["ann", "betty", "cindy"]), index.collect(["betty", "ann", "cindy"]))
        self.assertEqual(index.collect(["ann", "betty", "title"]), index.collect(["ann", "tom", "title"]))
