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
import functions.search
import functions.emotions
import utils.utils


app = flask.Flask(config.API_config.app_name)


@app.route("/autocomplete/", methods=['GET'], endpoint="autocomplete")
@api.basic.exception_handler
def autocomplete():
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text).lower()
    word_regex_list = [text for text in search_text.split(' ') if text]
    num = flask.request.args.get("number")
    if num is not None:
        num = int(num)
    return functions.suggest.suggest_autocomplete(word_regex_list, num), 200


@app.route("/similar_search/", methods=['GET'], endpoint="similar_search")
@api.basic.exception_handler
def similar_search():
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text).lower()
    word_regex_list = [text for text in search_text.split(' ') if text]
    num = flask.request.args.get("number")
    if num is not None:
        num = int(num)
    return functions.suggest.suggest_similar_search(word_regex_list, num), 200


# deprecated
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
    _id = int(flask.request.args.get("id"))
    search_text = flask.request.args.get("search_text")
    search_text = utils.utils.remove_wild_char(search_text).lower()
    word_regex_list = [text for text in search_text.split(' ') if text]
    length = flask.request.args.get("length")
    if length is not None:
        length = int(length)
    session = datasources.get_db().create_session()
    ans = functions.snippet.gen_snippet_with_wildcard(session, word_regex_list, _id, length)
    datasources.get_db().close_session(session)
    return ans, 200


@app.route("/search", methods=['GET'])
def search():
    query = flask.request.args.get("query")
    ranking = flask.request.args.get("ranking-by")
    page = flask.request.args.get('page')
    session = datasources.get_db().create_session()
    results_count, result_list, good_search_mode = functions.search.universal_search(session, query, int(ranking), int(page))
    datasources.get_db().close_session(session)
    return flask.jsonify({'results_count': results_count, 'result_list': result_list,
                          'good_search_mode': good_search_mode})


@app.route('/news', methods=['GET'])
def get_a_news():
    _id = int(flask.request.args.get('id'))
    session = datasources.get_db().create_session()
    if _id is not None:  # more fast
        news_detail = datasources.get_db().find_news_by_news_id(session, _id)
    else:
        return
    data = {'review_num': news_detail.review_num,
            'abstract': news_detail.abstract,
            'content': news_detail.content,
            'keywords': news_detail.keywords,
            'title': news_detail.title,
            'url': news_detail.url,
            'id': news_detail.id,
            'media_name': news_detail.media_name,
            'time': news_detail.time}
    datasources.get_db().close_session(session)
    return flask.jsonify(data)


@app.route('/suggnew/recommend_news', methods=['GET'])
def related_news():
    _id = int(flask.request.args.get('id'))

    session = datasources.get_db().create_session()

    data = functions.suggest.suggest_similar_news(session, _id)

    datasources.get_db().close_session(session)
    return flask.jsonify({'content': data})


@app.route('/news/review')
def get_review():
    new_id = int(flask.request.args.get('id'))
    session = datasources.get_db().create_session()
    r = datasources.get_db().find_reviews_by_news_id(session, int(new_id))
    datasources.get_db().close_session(session)
    data = [{'agree': review.agree, 'content': review.content,
             'emotion': functions.emotions.analyze_emotion4review(review.content)} for review in r]
    positive_counts = 0
    for review in data:
        positive_counts += review['emotion'] + 1  # negative: -1; positive : 0
    return flask.jsonify({'review': data, 'emotions': positive_counts*1.0/len(data)})


@app.route('/suggnew/hotnews')
def hotnews():
    page = int(flask.request.args.get('page'))
    session = datasources.get_db().create_session()
    r = functions.suggest.suggest_hot_news(session, page)
    datasources.get_db().close_session(session)
    return flask.jsonify({'content': r})


def run():
    config.spark_config.testing = False
    # Tell spark executor it is not a driver.
    config.spark_config.driver_mode = True
    th = threading.Thread(target=api.basic.backdoor)
    th.start()
    # disable autoreload to enable TRUE DEBUG!
    app.run(host=config.API_config.host, port=config.API_config.port,
            debug=False, use_reloader=False, use_debugger=False)
