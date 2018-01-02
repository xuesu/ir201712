#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask_api


class DEMOBaseException(Exception):
    """ This exception is a base of all resolver exception """

    def __init__(self, message, *args, **kwargs):
        super(DEMOBaseException, self).__init__(message, *args, **kwargs)
        self.error_code = "InternalServerError"
        self.status_code = flask_api.status.HTTP_500_INTERNAL_SERVER_ERROR
        self.ch_message = "服务器内部错误"

    def __str__(self):
        return "{0} error code: {1}, status code: {2}".format(
            self.message, self.error_code, self.status_code)