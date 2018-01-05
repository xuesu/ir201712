# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import copy
import itertools

import config
import indexes
import filters
import utils.decorator
import utils.utils
import datasources


@utils.decorator.timer
def suggest_autocomplete(word_regex_list, num=None):
    if num is None:
        num = config.functions_config.autocomplete_default_number
    candidate_texts = indexes.IndexHolder().word_text_index.collect(word_regex_list[-1])
    # candidates = filters.filter_by_avgtfidf(candidates, num * 2)
    # candidates_groups = [word_regex_list[: -1] + [candidate] for candidate in candidates]
    # candidates_groups = filters.filter_by_coocurrence(candidates_groups, num)
    # return [candidates[-1] for candidates in candidates_groups]
    candidate_texts = filters.filter_by_avgtfidf(candidate_texts, num)
    return candidate_texts


@utils.decorator.timer
def suggest_similar_search(word_regex_list, num=None):
    if num is None:
        num = config.functions_config.similar_search_default_number
    word_wildcard_list = [word_regex for word_regex in word_regex_list if '*' in word_regex]
    word_texts = [word_regex for word_regex in word_regex_list if '*' not in word_regex]
    length = config.functions_config.similar_search_candidate_length
    if word_wildcard_list:
        wildcard_groups = list()
        for word_text in word_wildcard_list:
            candidates = indexes.IndexHolder().word_text_index. \
                collect(word_text, action=indexes.IndexHolder().word_text_index.CollectionAction.SIMILAR)
            candidates = filters.filter_by_avgtfidf(candidates, config.functions_config.similar_search_candidate_number)
            if candidates:
                wildcard_groups.append(candidates)
        if wildcard_groups:
            wildcard_candidates_groups = [list(x) for x in itertools.product(*wildcard_groups)]
            if len(word_wildcard_list) >= length or not word_texts:
                # use wildcard only
                for i in range(len(wildcard_candidates_groups)):
                    wildcard_candidates_groups[i] = filters.filter_by_random(wildcard_candidates_groups[i], length)
            else:
                for i in range(len(wildcard_candidates_groups)):
                    wildcard_candidates_groups[i] += filters.filter_by_random(word_texts, length - len(word_wildcard_list))
            return filters.filter_by_coocurrence(wildcard_candidates_groups, num)
    candidates_groups = list()
    for i, word_text in enumerate(word_texts):
        other_words = word_texts[:i] + word_texts[i + 1:]
        candidates = indexes.IndexHolder().word_text_index. \
            collect(word_text, action=indexes.IndexHolder().word_text_index.CollectionAction.SIMILAR)
        candidates = filters.filter_by_avgtfidf(candidates, config.functions_config.similar_search_candidate_number)
        for candidate in candidates:
            if candidate == word_text:
                continue
            candidates_groups.append([candidate] + filters.filter_by_random(other_words, length - 1))
    return filters.filter_by_coocurrence(candidates_groups, num)


def suggest_similar_news(session, news_id):
    pass


def suggest_hot_news(session):
    """
    check that documents in redis(cache) is not expired 
    :param session: 
    :return: 
    """
    # check first.
    # if expired, we should construct 1000 hot news again
    EXPIRED = True
    if EXPIRED:
        r = datasources.get_db().find_hot_news(session, 1000)
        if len(r) > 10:
            candidate = r[:10]
        else:
            candidate = r

        cache = {news.source_id: {'title': news.title, 'abstract': news.abstract,
                                  'time': news.time, 'keywords': news.keywords} for news in r}
        candidate = [{'source_id': news.source_id, 'title': news.title, 'abstract': news.abstract,
                      'time': news.time, 'keywords': news.keywords} for news in candidate]

        # we should cache the variable cache into redis.
        return candidate
    else:  # to read redis.
        pass
