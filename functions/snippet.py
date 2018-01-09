# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import config
import datasources
import my_exceptions.datasources_exceptions
import functions.suggest
import update.segment
import utils.decorator


@utils.decorator.timer
def gen_snippet_with_wildcard(session, word_regex_list, news_id, length=None):
    fl = '*' in ''.join(word_regex_list)
    if fl:
        word_text_list = functions.suggest.suggest_similar_search(word_regex_list, 1)[0]
    else:
        word_text_list = word_regex_list
    return gen_snippet(session, word_text_list, news_id, length)


@utils.decorator.timer
def gen_snippet(session, word_text_list, news_id, length=None):
    if length is None:
        length = config.functions_config.snippet_max_length
    word_text_list = set(word_text_list)
    news = datasources.get_db().find_news_by_id(session, news_id)
    if news is None:
        raise my_exceptions.datasources_exceptions.NewsNotFoundException(news_id=news_id)
    abstract = news.abstract
    content = news.content
    stop_punc_list = {'。', '？', '！', '：', '；', '”', '“', '"', '…', '?', '!', '\n'}
    words = [('\n', 'x', 0)]
    mid_words = [(w[0], w[1], w[3]) for w in update.segment.tokenize(content, mode="search")
              if w[0] in stop_punc_list or w[0] in word_text_list]
    punc_near_words = [False] * len(mid_words)
    for i, word in enumerate(mid_words):
        punc_near_words[i] = True
        if word[0] not in stop_punc_list:
            for j in range(i + 1, len(mid_words)):
                if mid_words[j][2] - word[2] < length:
                    punc_near_words[j] = True
                else:
                    break
            for j in range(i - 1, 0, -1):
                if mid_words[j][2] - word[2] < length:
                    punc_near_words[j] = True
                else:
                    break
    mid_words = [mid_words[i] for i in range(len(mid_words)) if punc_near_words[i]]
    del punc_near_words
    words += mid_words
    word_num = len(words)
    words.append(('\n', 'x', len(content)))
    nums = dict()
    goal_s = 0
    goal_n = 0
    goal_dis = length
    goal_e = 0
    e = 0
    que = list()
    for s in range(word_num):
        while e < word_num and words[e + 1][2] - words[s][2] < length:
            if words[e][0] in word_text_list:
                nums[words[e][0]] = nums.get(words[e][0], 0) + 1
                que.append(words[e][2])
            e += 1
        if que:
            dis = que[0] - words[s][2]
        else:
            dis = length

        if words[s][0] in stop_punc_list:
            if len(nums) > goal_n or (len(nums) == goal_n and dis < goal_dis):
                goal_s = s
                goal_e = e
                goal_dis = dis
                goal_n = len(nums)
        else:
            if que and que[0] == words[s][2]:
                nums[words[s][0]] = nums.get(words[s][0], 0) - 1
                que = que[1:]
                if nums[words[s][0]] == 0:
                    nums.pop(words[s][0])
            if goal_n == 0:
                goal_s = s
                goal_e = goal_s
                goal_n = 0.5
        s += 1
        if e < s:
            e += 1
    if goal_s != goal_e:
        return content[words[goal_s][2]: words[goal_e][2]]
    elif goal_s != 0:
        return content[words[goal_s - 1][2]: words[goal_s - 1][2] + length]
    return abstract[:length]
