# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import flask
import threading
import traceback

import config.config_manager
import exceptions.base_exception
import functions.suggest
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


@app.route("/suggest", method='GET')
@exception_handler
def suggest():
    search_text = flask.request.args.get("search_text")
    return functions.suggest.suggest_autocomplete(search_text), 200


def run():
    th = threading.Thread(target=backdoor)
    th.start()
    # disable autoreload to enable TRUE DEBUG!
    app.run(host=APIconfig.host, port=APIconfig.port, debug=False, use_reloader=False, use_debugger=False)
