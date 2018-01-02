# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import exceptions.base_exception


class NewsNotFoundException(exceptions.base_exception.IRBaseException):
    def __init__(self, news_id):
        message = "Can not found news {}".format(news_id)
        super(NewsNotFoundException, self).__init__(message, status_code=404)
        self.news_id = news_id
