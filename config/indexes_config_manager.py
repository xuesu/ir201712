# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import os

cur_dir = os.path.realpath(__file__)[:-len("config/functions_config.py")]


class IndexesConfig(object):
    def __init__(self, config_data):
        self.word_synonym_default_number = config_data["word_synonym"]["default_number"]
        word_synonym_model_cache_path = config_data["word_synonym"]["model_cache_path"]
        if os.path.isabs(word_synonym_model_cache_path):
            self.word_synonym_model_cache_path = word_synonym_model_cache_path
        else:
            self.word_synonym_model_cache_path = os.path.join(cur_dir, word_synonym_model_cache_path)
