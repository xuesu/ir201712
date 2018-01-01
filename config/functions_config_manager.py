# -*- coding:utf-8 -*-
"""
@author: xuesu
"""


class FunctionsConfig(object):
    def __init__(self, config_data):
        self.autocomplete_default_number = int(config_data['autocomplete']['default_number'])
        self.similar_search_default_number = int(config_data['similar_search']['default_number'])
        self.similar_search_candidate_number = int(config_data['similar_search']['candidate_number'])
        self.snippet_max_length = int(config_data['snippet']['max_length'])
