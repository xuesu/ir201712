# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""
import functions.suggest
import indexes
import test


class SuggestTest(test.TestCase):
    def setUp(self):
        test.runSQL()
        indexes.IndexHolder().init(True)

    def tearDown(self):
        pass

    def test_suggest_autocomplete(self):
        candidates = functions.suggest.suggest_autocomplete(["护"], num=3)
        self.assertIn("护士", candidates)

    def test_suggest_similar_search(self):
        candidate_groups = functions.suggest.suggest_similar_search(["浙江", "毒苹果", "女士", "快递", "开门"], num=3)
        self.assertEqual(len(candidate_groups), 3)

        candidate_groups = functions.suggest.suggest_similar_search(["浙江", "毒*果", "女士", "快递", "开门"], num=3)
        self.assertEqual(len(candidate_groups), 3)

        candidate_groups = functions.suggest.suggest_similar_search(["BBBBBBBBBBBB", "UUUUUUUUUU"], num=3)
        self.assertEqual(len(candidate_groups), 0)

        candidate_groups = functions.suggest.suggest_similar_search(["BBBBBBB*", "女士"], num=3)
        self.assertEqual(len(candidate_groups[0]), 1)
