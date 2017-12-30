import copy

import config
import indexes
import sorter


def suggest_autocomplete(word_regex_list):
    function_config = config.functions_config
    candidates = indexes.IndexHolder().word_index.collect(word_regex_list[-1])
    candidates = sorter.sort_by_avgtfidf(candidates, function_config.suggest_num)
    return [word.text for word in candidates]


def suggest_similar_keywords(word_regex_list):
    candidates_groups = [[]]
    for word_regex in word_regex_list:
        if '*' in word_regex:
            candidates = indexes.IndexHolder().word_index.collect(word_regex)
        else:
            candidates = indexes.IndexHolder().word_synonym_index.collect(word_regex)
        new_candidates_groups = []
        for keywords in candidates_groups:
            for word in candidates:
                new_candidates_groups.append(copy.deepcopy(keywords))
                new_candidates_groups[-1].append(word)
    return candidates_groups
