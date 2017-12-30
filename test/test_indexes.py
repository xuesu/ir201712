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
        index.build()
        self.assertIsNotNone(index.collect("10"))
        self.assertEqual(len(index.collect("10").posting_list), 0)
        self.assertIsNone(index.collect("a"))

    def test_word_text_index(self):
        word_text_samples = ["1000", "10", "001", "010", "0", "1", "01"]
        for word_text in word_text_samples:
            datasources.get_db().upsert_word_or_word_list(self.session, entities.words.Word(text=word_text))
        index = indexes.word_text_index.WordTextIndex()
        index.build()
        word_texts = index.collect()
        word_texts.sort()
        word_text_samples.sort()
        self.assertListEqual(word_texts, word_text_samples)

    def test_posting_index(self):
        news_list = [entities.news.NewsPlain(source_id=1), entities.news.NewsPlain(source_id=2)]
        news_list = datasources.get_db().upsert_news_or_news_list(self.session, news_list)
        word_posting_list = [entities.words.WordPosting(news_id=news_list[0].id),
                             entities.words.WordPosting(news_id=news_list[0].id),
                             entities.words.WordPosting(news_id=news_list[1].id)]
        words_list = [entities.words.Word(text="a"), entities.words.Word(text="b")]
        words_list[0].posting_list = word_posting_list[:1]
        words_list[1].posting_list = word_posting_list[1:]
        words_list = datasources.get_db().upsert_word_or_word_list(self.session, words_list)
        index = indexes.posting_index.PostingIndex()
        index.build()
        self.assertEqual(len(index.collect([words_list[0].id, words_list[1].id], index.LogicAction.OR)), 2)
        self.assertEqual(len(index.collect([words_list[0].id, words_list[1].id], index.LogicAction.AND)), 1)
