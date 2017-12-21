# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import flask

import config.config_manager
import exceptions.base_exception
import logs.loggers

logger = logs.loggers.LoggersHolder().get_logger('api')
APIconfig = config.config_manager.ConfigManager().APIconfig
app = flask.Flask(APIconfig.app_name)

ERR_MESSAGE_HTTP_500 = "Unknown Internal Server Error: {}."


def exception_handler(method):
    def wrapper(*args, **kwargs):
        try:
            content, status_code = method(*args, **kwargs)
            resp = flask.jsonify({"content": content})
            resp.status_code = status_code
        except exceptions.base_exception.IRBaseException as e:
            resp = flask.jsonify({"err_message": e.message})
            resp.status_code = e.status_code
            logger.info(e.message, exc_info=False)
        except Exception as e:
            resp = flask.jsonify({"err_message": ERR_MESSAGE_HTTP_500.format(type(e))})
            resp.status_code = 500
            logger.error(ERR_MESSAGE_HTTP_500, exc_info=True)
        return resp

    return wrapper


def run():
    # disable autoreload to enable TRUE DEBUG!
    app.run(host=APIconfig.host, port=APIconfig.port, debug=False, use_reloader=False, use_debugger=False)
