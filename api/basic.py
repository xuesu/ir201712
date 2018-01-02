# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import flask
import traceback

import my_exceptions.base_exception
import logs.loggers

logger = logs.loggers.LoggersHolder().get_logger('api')

ERR_MESSAGE_HTTP_500 = "Unknown Internal Server Error: {}."


def exception_handler(method):
    def wrapper(*args, **kwargs):
        try:
            content, status_code = method(*args, **kwargs)
            resp = flask.jsonify({"content": content})
            resp.status_code = status_code
        except my_exceptions.base_exception.IRBaseException as e:
            resp = flask.jsonify({"err_message": e.message})
            resp.status_code = e.status_code
            logger.info(e.message, exc_info=False)
        except Exception as e:
            resp = flask.jsonify({"err_message": ERR_MESSAGE_HTTP_500.format(type(e))})
            resp.status_code = 500
            logger.error(ERR_MESSAGE_HTTP_500.format(type(e)), exc_info=True)
        return resp

    return wrapper


def backdoor():
    """
    Aim to execute refresh.
    :return:
    """
    command = ''
    while True:
        tmp = input()
        command += tmp
        if command == 'STOP BACKDOOR;':
            break
        elif command.endswith(';'):
            try:
                command = command[:-1]
                exec(command)
            except Exception as e:
                traceback.print_exc()
            command = ''
