# -*- coding:utf-8 -*-
"""
@author: xuesu
"""

import os

cur_dir = os.path.realpath(__file__)[:-len("config/indexes_config_manager.py")]


class IndexesConfig(object):
    def __init__(self, config_data):
        word_synonym_config = config_data["word_synonym"]
        self.word_synonym_default_number = word_synonym_config["default_number"]
        word_synonym_model_cache_path = word_synonym_config["model_cache_path"]
        if os.path.isabs(word_synonym_model_cache_path):
            self.word_synonym_model_cache_path = word_synonym_model_cache_path
        else:
            self.word_synonym_model_cache_path = os.path.join(cur_dir, word_synonym_model_cache_path)
        word_text_config = config_data["word_text"]
        word_text_similar_config = word_text_config["similar"]
        self.word_text_similar_default_threshold = word_text_similar_config["default_threshold"]
        self.word_text_similar_penalties = word_text_similar_config["penalties"]
        word_cooccurrence_config = config_data["word_cooccurrence"]
        word_cooccurrence_model_cache_path = word_cooccurrence_config["model_cache_path"]
        if os.path.isabs(word_cooccurrence_model_cache_path):
            self.word_cooccurrence_model_cache_path = word_cooccurrence_model_cache_path
        else:
            self.word_cooccurrence_model_cache_path = os.path.join(cur_dir, word_cooccurrence_model_cache_path)
