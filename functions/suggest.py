# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import copy

import config
import indexes
import filters
import utils.decorator


@utils.decorator.timer
def suggest_autocomplete(session, word_regex_list, num=None):
    if num is None:
        num = config.functions_config.autocomplete_default_number
    candidate_texts = indexes.IndexHolder().word_index.collect(word_regex_list[-1])
    candidates = indexes.IndexHolder().vocab_index.collect(candidate_texts)
    # candidates = filters.filter_by_avgtfidf(candidates, num * 2)
    # candidates_groups = [word_regex_list[: -1] + [candidate] for candidate in candidates]
    # candidates_groups = filters.filter_by_coocurrence(candidates_groups, num)
    # return [candidates[-1] for candidates in candidates_groups]
    candidates = filters.filter_by_avgtfidf(candidates, num)
    return [word.text for word in candidates]


@utils.decorator.timer
def suggest_similar_search(session, word_regex_list, num=None):
    if num is None:
        num = config.functions_config.similar_search_default_number
    candidates_groups = [[]]
    for word_regex in word_regex_list:
        candidates = indexes.IndexHolder().word_index. \
            collect(word_regex, action=indexes.IndexHolder().word_index.CollectionAction.SIMILAR)
        candidates = filters.filter_by_avgtfidf(candidates, config.functions_config.similar_search_candidate_number)
        new_candidates_groups = []
        for keywords in candidates_groups:
            for word in candidates:
                new_candidates_groups.append(copy.deepcopy(keywords))
                new_candidates_groups[-1].append(word)
    candidates_groups = filters.filter_by_coocurrence(candidates_groups, num)
    return candidates_groups


def suggest_similar_news(session, news_id):
    pass
