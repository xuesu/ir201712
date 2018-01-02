# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import flask
import threading

import api.basic
import config
import datasources
import functions.emotions
import functions.snippet
import functions.suggest
import utils.utils


app = flask.Flask(config.API_config.app_name)


@app.route("/autocomplete/", methods=['GET'], endpoint="autocomplete")
@api.basic.exception_handler
def autocomplete():
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text)
    word_regex_list = search_text.split(' ')
    num = flask.request.args.get("number")
    if num is not None:
        num = int(num)
    return functions.suggest.suggest_autocomplete(word_regex_list, num), 200


@app.route("/similar_search/", methods=['GET'], endpoint="similar_search")
@api.basic.exception_handler
def similar_search():
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text)
    word_regex_list = search_text.split(' ')
    num = flask.request.args.get("number")
    if num is not None:
        num = int(num)
    return functions.suggest.suggest_similar_search(word_regex_list, num), 200


@app.route("/emotions/", methods=['GET'], endpoint="emotions")
@api.basic.exception_handler
def analyze_emotion4news():
    news_id = int(flask.request.args.get("news_id"))
    session = datasources.get_db().create_session()
    ans = functions.emotions.analyze_emotion4news(session, news_id)
    datasources.get_db().close_session(session)
    return ans, 200


@app.route("/snippet/", methods=['GET'], endpoint="snippet")
@api.basic.exception_handler
def get_snippet():
    news_id = int(flask.request.args.get("news_id"))
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text)
    word_regex_list = search_text.split(' ')
    length = flask.request.args.get("length")
    if length is not None:
        length = int(length)
    session = datasources.get_db().create_session()
    ans = functions.snippet.gen_snippet_with_wildcard(session, word_regex_list, news_id, length)
    datasources.get_db().close_session(session)
    return ans, 200


def run():
    th = threading.Thread(target=api.basic.backdoor)
    th.start()
    # disable autoreload to enable TRUE DEBUG!
    app.run(host=config.API_config.host, port=config.API_config.port,
            debug=False, use_reloader=False, use_debugger=False)
