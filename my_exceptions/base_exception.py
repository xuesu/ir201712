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


class InvalidParameterIRException(IRBaseException):
    def __init__(self, func, param_name, valid_type, actual_value):
        message = "{}: Param {} should receive an instance of {}, but got {} of type {}.".format(func, param_name,
                                                                                                 valid_type,
                                                                                                 actual_value,
                                                                                                 type(actual_value))
        super(InvalidParameterIRException, self).__init__(message)
        self.func = func
        self.param_name = param_name
        self.valid_type = valid_type
        self.actual_value = actual_value


class RequriedParameterEmpty(IRBaseException):
    def __init__(self, func, param_name):
        message = "{}: Param {} is None.".format(func, param_name)
        super(RequriedParameterEmpty, self).__init__(message)
        self.func = func
        self.param_name = param_name
