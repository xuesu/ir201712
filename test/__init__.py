# -*- coding:utf-8 -*-
"""
@author: xuesu

used to prepare testcase environment
"""

import unittest

import config


class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        config.spark_config.testing = True
