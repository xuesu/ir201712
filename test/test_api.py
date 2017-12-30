# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import flask

import api.api
import exceptions.base_exception
import test


class APITest(test.TestCase):
    def setUp(self):
        self.app = flask.Flask("test")
        self.app.testing = True

    def tearDown(self):
        pass

    def test_exception_handler(self):
        @api.api.exception_handler
        def test_500():
            raise ValueError()

        @api.api.exception_handler
        def test_300():
            raise exceptions.base_exception.IRBaseException("This is an err!")

        @api.api.exception_handler
        def test_233():
            return {}, 233

        with self.app.test_request_context():
            resp = test_500()
            self.assertEqual(resp.status_code, 500)

            resp = test_300()
            self.assertEqual(resp.status_code, 300)

            resp = test_233()
            # decorator will change return type.
            self.assertEqual(resp.status_code, 233)
