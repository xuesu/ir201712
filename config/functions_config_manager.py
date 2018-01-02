# -*- coding:utf-8 -*-
"""
@author: xuesu
"""


class FunctionsConfig(object):
    def __init__(self, config_data):
        self.autocomplete_default_number = int(config_data['autocomplete']['default_number'])
        self.similar_search_default_number = int(config_data['similar_search']['default_number'])
        self.similar_search_candidate_number = int(config_data['similar_search']['candidate_number'])
        self.similar_search_candidate_length = int(config_data['similar_search']['candidate_length'])
        self.similar_search_candidate_replace_times = int(config_data['similar_search']['candidate_replace_times'])
        self.snippet_max_length = int(config_data['snippet']['max_length'])
        self.emotions_host = config_data['emotions']['host']
        self.emotions_port = config_data['emotions']['port']
        self.emotions_url = 'http://{}:{}/predict/'.format(self.emotions_host, self.emotions_port)
