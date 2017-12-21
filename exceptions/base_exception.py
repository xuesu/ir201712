# -*- coding:utf-8 -*-
"""
@author: xuesu

ALL SELF-DEFINED EXCEPTIONS MUST INHERIT IRBaseException!
"""


class IRBaseException(Exception):
    """
    ALL SELF-DEFINED EXCEPTIONS MUST INHERIT IRBaseException!
    Aims to distinguish predictable Exceptions.
    """

    def __init__(self, message, status_code=None, *args):
        """
        :param message: prompt in the http response
        :param status_code: status code in the http response, default is 300
        """
        super(IRBaseException, self).__init__(*args)
        self.message = message
        if status_code is None:
            self.status_code = 300
        else:
            self.status_code = status_code
