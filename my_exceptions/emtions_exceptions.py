# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import my_exceptions.base_exception


class EmotionRequestError(my_exceptions.base_exception.IRBaseException):
    def __init__(self, sube):
        message = "EmotionRequestError caused by: {}".format(sube)
        super(EmotionRequestError, self).__init__(message)
        self.sube = sube
