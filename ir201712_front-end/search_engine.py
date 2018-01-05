# -*- coding:utf-8 -*-
"""
@author: rickllyxu

"""
from flask import Flask, render_template, request, jsonify, session, escape
import sys
import time
import json
import requests
reload(sys)
sys.setdefaultencoding('utf8')
app = Flask(__name__)

RELEVENCE_RANKING = 1
TIME_DESCEND_RANKING = 2
TIME_INCREASE_RANKING = 3
HOT_RANKING = 4


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
    print 'paras for searching: ', paras
    print 'starting to searching...'
    resp = requests.get("localhost:8888/search", params=paras)
    # parse the resp and render html.

    data = resp.content
    for r in data['result_list']:
        r['fake_url'] = '/news?news_id=' + r['news_id']
    data['currentpage'] = int(paras['page'])
    data['pages'] = 10 if len(data['results_count'])/10 > 10 else len(data['results_count'])/10 + 1
    data['query'] = request.args.get('query')
    data['time_cost'] = time.time() - _start_t
    data['sortby'] = paras['ranking-by']
    print 'search result: ', data
    return render_template('result.html', data=data)


@app.route('/search/snippet')
def get_snippet():
    _id = request.args.get('id')
    if _id is None:
        return
    search_text = request.args.get('search_text')
    resp = requests.get("localhost:8888/snippet", {'news_id': _id, 'search_text': search_text})
    print 'snippet: ', resp.content
    return resp.content


@app.route('/suggnew/recommend_searchwords')
def recommend_searchwords():
    search_text = request.args.get('search_text')
    resp = requests.get('localhost:8888/similar_search', {'search_text': search_text})
    print 'recommend search words:', resp.content
    return resp.content


@app.route('/news')
def news():
    """
    news preview page. 
    GET /news?news_id=<string>
    Each news has following attributes: source,news_id,url,title,keywords,
    media_name,abstract,content,time,review_num,related_id
    Here I may attach a new attr to it: preview_url = '/news?news_id=%s'.format(news_id)
    持有该news_id到mysql中查询, 
    :return: data包含该篇文章 [及对应的推荐新闻，也可单独请求]  
    评论及情感色彩异步加载， 推荐新闻也异步请求。
    """
    news_id = request.args.get('news_id', 'fake-0000')
    resp = requests.get('localhost:8888/news', {'news_id': news_id})
    print 'detail of the news: ', resp.content
    return render_template('news_preview.html', data=resp.content)


@app.route('/suggnew/recommend_news')
def recommend_news():
    """
    GET /suggnew/recommend_news?related_id=<string>
    拿着original_news_id去找该新闻的相似[推荐]新闻
    目前是直接用related_id.
    :return: 
    """
    NAVIVE_METHOD = True
    if NAVIVE_METHOD:
        related_id = request.args.get('related_id')
        if related_id.strip() == "":
            return
        resp = requests.get('localhost:8888/suggnew/recommend_news', related_id=related_id)
        print 'recommend news and their source id', resp.content
        return resp.content
    else:
        raise NotImplementedError


@app.route('/news/review')
def get_review():
    _id = request.args.get('id')
    if _id is None:
        return
    resp = requests.get('localhost:8888/news/review', _d=_id)
    print 'review and their emotions:', resp.content
    return resp.content


@app.route('/suggnew/word_completion')
def word_completion():
    """
    用户输入一个词字后推荐补齐。按照下述格式返回才行。
    :return: 
    """
    key = request.args.get('key')
    resp = requests.get('localhost:8888/autocomplete/', search_text=key)
    comlete_list = resp.content['content']
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
    top_words = ['王斌教授发了CCF A类会议', '比特币暴涨', '何以解忧？唯有..']
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
    resp = requests.get('localhost:8888/suggnew/hotnews', page=page)

    data = resp.content['content']
    print 'hot news: ', data
    for r in data:
        r['news_id'] = r['source_id'].pop()
        r['fake_url'] = '/news?news_id=' + r['news_id']
        r['behot_time'] = r['time'].pop()
        r['brief'] = r['abstract'].pop()

    news_format = dict()
    news_format['news_id'] = 'fake000001'
    news_format['title'] = '我们'
    news_format['source'] = 'source'
    news_format['preview_url'] = '/news?news_id=' + news_format['news_id']
    news_format['brief'] = 'brief'
    news_format['behot_time'] = '10:10'

    response['data'] = data
    return jsonify(response)


# deprecated
# QA snippet, the most relevent answer
@app.route('/suggnew/gosugg')
def sugg_answer():
    return None

if __name__ == '__main__':
    app.secret_key = 'AT8*3Kf?!@JOEWKHldfsdoei'
    app.run(debug=True)
