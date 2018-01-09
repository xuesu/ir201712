# -*- coding:utf-8 -*-
"""
@author: xuesu
Do not import config.config_manager here.

"""

import copy
import datetime
import itertools
import re


def get_date_before(shift=0):
    # 返回当前日期shift天后的日期，正数代表将来，负数代表过去，格式：‘2017-11-15’
    now_time = datetime.datetime.now()
    date = now_time - datetime.timedelta(days=shift)
    return date.strftime('%Y-%m-%d')


def remove_wild_char(s):
    if s is not None:
        s = re.sub(r"[^\s\w`=\\;.!/_,$^*+\"\'\[\]—！，。？、~@#￥%…&（）：；《》“”()»〔〕?\-]", "", s)
        s = re.sub("\r", "\n", s)
        s = re.sub("\n\n", "\n", s)
        s = re.sub("\n +", "\n", s)
        return s.strip()
    return ''


def remove_wild_char_in_news(news):
    news.title = remove_wild_char(news.title)
    news.content = remove_wild_char(news.content)
    news.abstract = remove_wild_char(news.abstract)
    news.keywords = remove_wild_char(news.keywords)
    news.media_name = news.media_name.strip()[:19]
    for review in news.reviews:
        remove_wild_char_in_review(review)


def remove_wild_char_in_review(review):
    review.content = remove_wild_char(review.content)
    review.user_name = remove_wild_char(review.user_name)


def remove_new_line(s):
    s = re.sub("[\n|\r]", " ", s)
    return s.strip()


def merge_dict_using_bigger_v(d1, d2):
    d3 = {k: d1[k] for k in d1}
    for k in d2:
        if d1.get(k) is None:
            d3[k] = d2[k]
        else:
            d3[k] = max(d1[k], d2[k])
    return d3


def merge_two_str(s1, s2):
    if s1 < s2:
        return s1 + " " + s2
    return s2 + " " + s1


def replace_partial_list(l1, mat, t):
    l1 = copy.deepcopy(l1)
    res = list()
    out_idxes = [i for i in range(len(l1))]
    in_idxes = [i for i in range(len(mat))]
    for sout_idxes, sin_idxes in itertools.product(itertools.combinations(out_idxes, t),
                                                   itertools.combinations(in_idxes, t)):
        in_mat = [mat[sin_idx] for sin_idx in sin_idxes]
        for in_vec in itertools.product(in_mat):
            for i in range(t):
                l1[sout_idxes[i]] = in_vec[i]
            res.append(copy.deepcopy(res))


def parse_timestr(timestr):
    for time_format in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M']:
        try:
            time = datetime.datetime.strptime(timestr, time_format)
            return time
        except ValueError:
            pass
    raise ValueError()
