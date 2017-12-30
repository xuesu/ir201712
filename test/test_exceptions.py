# -*- coding:utf-8 -*-
"""
@author: xuesu

be lazy, be in one script
"""

import exceptions.base_exception
import test


class IRBaseExceptionTest(test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        mes = "An err!"
        exp = exceptions.base_exception.IRBaseException(mes)
        self.assertEqual(mes, exp.message)
        self.assertEqual(300, exp.status_code)
        exp = exceptions.base_exception.IRBaseException(mes, 500)
        self.assertEqual(500, exp.status_code)
