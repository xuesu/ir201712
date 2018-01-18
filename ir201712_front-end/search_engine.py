# -*- coding:utf-8 -*-
"""
@author: rickllyxu

"""
from flask import Flask, render_template, request, jsonify, session, escape
import sys
import time
import json
import requests
app = Flask(__name__)

RELEVENCE_RANKING = 1
TIME_DESCEND_RANKING = 2
TIME_INCREASE_RANKING = 3
HOT_RANKING = 4
URL = "http://0.0.0.0:8888"

@app.route('/')
def index():
    """
    main page
    GET /
    :return: 
    """
    return render_template('index.html')


@app.route('/search')
def search():
    """
    result list page
    GET /search?query=<string>&[some other paras]
    ps. 'ranking-by' is stored in cookies. 
    判断是否为通配符查询，使用不同的api
    :return: 搜索结果的列表 + 推荐搜索词 + 所花时间。 
    # 相关搜索推荐 使用异步加载技术
    # snippet生成 也采用异步加载
    """
    _start_t = time.time()
    paras = dict()
    paras.update({"query": request.args.get("query")})
    paras.update({'ranking-by': int(request.cookies.get('ranking-by', RELEVENCE_RANKING))})
    paras.update({'page': request.args.get('page', 1)})
    if paras['query'] == "":
        return
    print('paras for searching: ', paras)
    print('starting to searching...')
    resp = requests.get(URL + "/search", params=paras)
    # parse the resp and render html.

    data = json.loads(resp.content)
    data['result_list_2'] = []
    for r in data['result_list']:
        r['fake_url'] = '/news?id=' + str(r['id'])
        data['result_list_2'].append({'id': r['id'], 'good_search_mode': data['good_search_mode'][0]})
    data['currentpage'] = int(paras['page'])
    data['pages'] = 10 if data['results_count']/10 > 10 else data['results_count']/10 + 1
    data['query'] = request.args.get('query')
    data['time_cost'] = time.time() - _start_t
    data['sortby'] = paras['ranking-by']
    data['result_list_2'] = json.dumps(data['result_list_2'])
    return render_template('result.html', data=data)


@app.route('/search/snippet')
def get_snippet():
    _id = request.args.get('id')
    if _id is None:
        return
    search_text = request.args.get('search_text')
    resp = requests.get(URL + "/snippet", {'id': _id, 'search_text': search_text})

    return resp.content


@app.route('/suggnew/recommend_searchwords')
def recommend_searchwords():
    search_text = request.args.get('search_text')
    resp = requests.get(URL + '/similar_search', {'search_text': search_text})
    print(resp.content)
    return resp.content


@app.route('/news')
def news():
    """
    news preview page. 
    GET /news?id=<string>
    :return: data包含该篇文章 [及对应的推荐新闻，也可单独请求]  
    评论及情感色彩异步加载， 推荐新闻也异步请求。
    """
    _id = request.args.get('id', '1')
    resp = requests.get(URL + '/news', {'id': _id})
    return render_template('news_preview.html', data=json.loads(resp.content))


@app.route('/suggnew/recommend_news')
def recommend_news():
    _id = request.args.get('id')
    if _id is None:
        return jsonify([])
    resp = requests.get(URL + '/suggnew/recommend_news', {'id': _id})
    data = json.loads(resp.content)
    for r in data['content']:
        r['fake_url'] = "/news?id=" + str(r['id'])
    return jsonify(data)


@app.route('/news/review')
def get_review():
    _id = request.args.get('id')
    print(_id)
    if _id is None:
        return
    resp = requests.get(URL + '/news/review', params={'id': _id})
    # print 'review and their emotions:', json.loads(resp.content)
    return resp.content


@app.route('/suggnew/word_completion')
def word_completion():
    """
    用户输入一个词字后推荐补齐。按照下述格式返回才行。
    :return: 
    """
    key = request.args.get('key')
    resp = requests.get(URL + '/autocomplete/', {'search_text': key})
    data = json.loads(resp.content)
    comlete_list = data['content']
    no_sense_2 = ["0;0;0;0"] * len(comlete_list)
    no_sense_3 = [""] * len(comlete_list)
    comlete_str = json.dumps([key, comlete_list, no_sense_2, no_sense_3, ["0"],"","suglabId_1"])
    _format = "window.sogou.sug(%s,-1);" % comlete_str
    return _format


@app.route('/suggnew/hotwords')
def hotwords():
    """
    最热新闻中的关键词表里 (名词+动词) 的集合
    :return: 
    """
    top_words = ['王斌教授发了CCF A类会议', '比特币 暴涨', '何以解忧？唯有..']
    top_words_str = json.dumps(top_words)
    return "var top_words = %s" % top_words_str


@app.route('/suggnew/hotnews')
def hotnews():
    """
    最热新闻的定义是：过去一天以内，review_num最大的
    :return: 
    """
    page = int(request.args.get('page', 1))
    response = {'message': 'success', 'data': [], 'page': page + 1, 'ret': 0}
    # db_session = datasources.get_db().create_session()
    # hotnews_list = functions.hot.hot_news(db_session, (page-1)*10, 10)
    # FIXME: need to reformat each element.
    resp = requests.get(URL + '/suggnew/hotnews', {'page': page})

    data = json.loads(resp.content)['content']

    for r in data:
        r['fake_url'] = '/news?id=' + str(r['id'])
        r['behot_time'] = r.pop('time')
        r['brief'] = r.pop('abstract')

    response['data'] = data
    return jsonify(response)


# deprecated
# QA snippet, the most relevent answer
@app.route('/suggnew/gosugg')
def sugg_answer():
    return None

if __name__ == '__main__':
    app.secret_key = 'AT8*3Kf?!@JOEWKHldfsdoei'
    app.run(host="0.0.0.0", debug=True)
