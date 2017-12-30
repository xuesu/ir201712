# -*- coding:utf-8 -*-
"""
@author: xuesu

"""

import flask
import threading
import traceback

import config
import exceptions.base_exception
import functions.suggest
import logs.loggers
import utils.utils

logger = logs.loggers.LoggersHolder().get_logger('api')
app = flask.Flask(config.API_config.app_name)

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


@exception_handler
@app.route("/autocomplete", methods=['GET'])
def autocomplete():
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text)
    words_regex_list = search_text.split(' ')
    return functions.suggest.suggest_autocomplete(words_regex_list), 200


@exception_handler
@app.route("/keywords", methods=['GET'])
def similar_keywords():
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text)
    words_regex_list = search_text.split(' ')
    return functions.suggest.suggest_similar_keywords(words_regex_list), 200


def run():
    th = threading.Thread(target=backdoor)
    th.start()
    # disable autoreload to enable TRUE DEBUG!
    app.run(host=config.API_config.host, port=config.API_config.port,
            debug=False, use_reloader=False, use_debugger=False)
