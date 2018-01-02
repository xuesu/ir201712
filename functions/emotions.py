# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import requests
import simplejson as json

import config
import datasources
import my_exceptions.datasources_exceptions
import my_exceptions.emtions_exceptions


def analyze_emotion4news(session, news_id):
    news = datasources.get_db().find_news_by_id(session, news_id)
    if news is None:
        raise my_exceptions.datasources_exceptions.NewsNotFoundException(news_id)
    ans = list()
    for review in news.reviews:
        ans.append(analyze_emotion4review(review.content))
    return ans


def analyze_emotion4review(text):
    """
    :param text:
    :return: integer, -1: negative, 0: positive, cnn model based on NLPCC2014 no neural result because training data.
    """
    try:
        prompt_500 = "Unknown Restful Server Error"
        resp = requests.post(config.functions_config.emotions_url, data={"text": text})
        if resp.status_code == 500:
            raise my_exceptions.emtions_exceptions.EmotionRequestError(prompt_500)
        content = json.loads(resp.content)
        if resp.status_code // 100 != 2:
            raise my_exceptions.emtions_exceptions.EmotionRequestError(
                content.get("error", {"message": prompt_500}).get("message", prompt_500))
        return content['data']['tag']
    except Exception as e:
        raise my_exceptions.emtions_exceptions.EmotionRequestError(e)
