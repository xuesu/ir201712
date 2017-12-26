# -*- coding:utf-8 -*-
"""
@author: xuesu
Do not import config.config_manager here.

"""

import datetime
import re


def get_date_before(shift=0):
    # 返回当前日期shift天后的日期，正数代表将来，负数代表过去，格式：‘2017-11-15’
    now_time = datetime.datetime.now()
    date = now_time + datetime.timedelta(days=shift)
    return date.strftime('%Y-%m-%d')


def remove_wild_char(s):
    s = re.sub(r"[^\s\w`=\\;.!/_,$^*+\"\'\[\]—！，。？、~@#￥%…&（）：；《》“”()»〔〕?\-]", "", s)
    s = re.sub(r"[\s]", " ", s)
    s = re.sub(r"  ", " ", s)
    return s.strip()


def remove_wild_char_in_news(news):
    news.title = remove_wild_char(news.title)
    news.content = remove_wild_char(news.content)
    news.abstract = remove_wild_char(news.abstract)
    news.keywords = remove_wild_char(news.keywords)
    for review in news.reviews:
        remove_wild_char_in_review(review)


def remove_wild_char_in_review(review):
    review.content = remove_wild_char(review.content)


