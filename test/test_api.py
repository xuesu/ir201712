# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import api
import api.basic
import exceptions.base_exception
import test


class APITest(test.TestCase):
    def setUp(self):
        self.app = api.app.test_client()
        self.app.testing = True
        test.runSQL()

    def tearDown(self):
        pass

    def test_exception_handler(self):
        @api.basic.exception_handler
        def test_500():
            raise ValueError()

        @api.basic.exception_handler
        def test_300():
            raise exceptions.base_exception.IRBaseException("This is an err!")

        @api.basic.exception_handler
        def test_233():
            return {}, 233

        with api.app.test_request_context():
            resp = test_500()
            self.assertEqual(resp.status_code, 500)

            resp = test_300()
            self.assertEqual(resp.status_code, 300)

            resp = test_233()
            # decorator will change return type.
            self.assertEqual(resp.status_code, 233)

    def test_suggest_gen_snippet(self):
        resp = self.app.get("/snippet/", query_string={"search_text": "护士 直播", "length": 15, "news_id": 1})
        print(resp.data)
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get("/snippet/", query_string={"search_text": "护* 直播", "length": 15, "news_id": 1})
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get("/snippet/", query_string={"search_text": "护士 直播", "length": 15, "news_id": -100})
        self.assertEqual(resp.status_code, 404)

    def test_suggest_similar_search(self):
        resp = self.app.get("/similar_search/", query_string={"search_text": "护士 直播", "number": 3})
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get("/similar_search/", query_string={"search_text": "护* 直播", "number": 3})
        print(resp.data)
        self.assertEqual(resp.status_code, 200)

    def test_autocomplete(self):
        resp = self.app.get("/autocomplete/", query_string={"search_text": "护士 直", "number": 3})
        print(resp.data)
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get("/autocomplete/", query_string={"search_text": "护* 直", "number": 3})
        self.assertEqual(resp.status_code, 200)

    def test_analyze_emotion4news(self):
        resp = self.app.get("/emotions/", query_string={"news_id": 1})
        print(resp.data)
        self.assertEqual(resp.status_code, 200)
        resp = self.app.get("/emotions/", query_string={"news_id": -100})
        self.assertEqual(resp.status_code, 404)


