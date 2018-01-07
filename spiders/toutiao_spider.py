# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import bs4
import datetime
import demjson
import simplejson as json
import random
import time

import datasources
import entities.news
import entities.review
import logs.loggers
import spiders.base_spider
import utils.utils

logger = logs.loggers.LoggersHolder().get_logger("spiders")


class ToutiaoSpider(spiders.base_spider.BaseSpider):
    def __init__(self):
        super(ToutiaoSpider, self).__init__()
        self.toutiao_news_roll_url = r'https://www.toutiao.com/api/pc/feed/?category=news_society&utm_source=toutiao&widen=1&max_behot_time={}&max_behot_time_tmp={}&tadrequire=true&as=A125BA93E6A7F96&cp=5A3697EF09466E1&_signature=kuBu4QAAyOGy.bX4veRHx5Lgbv'
        # group_id={}&item_id={}
        self.toutiao_review_roll_url = r'https://www.toutiao.com/api/comment/list/?group_id={}&item_id={}&offset=0&count=20'
        self.toutiao_num = 30000
        self.toutiao_each_page_num = 7

    def get_news(self, news_num):
        """
        '获取如下数据：
            '获取新闻数据：
                source_id:新闻id,
                url:新闻链接,
                title:新闻标题,
                keywords:新闻关键词,
                media_name:发布媒体名称,
                abstract:新闻摘要,
                time:发布时间,
                news_content:新闻内容,
                review_num:评论条数
            '相关新闻数据:related_id:相关的新闻id列表
            '评论数据:
                user_id:用户id,
                user_name:用户昵称,
                area:评论地点,
                review_content:评论内容,
                time:评论时间,
                agree:点赞数
        """
        session = datasources.get_db().create_session()
        news_count = 0
        now_time = int(time.time())
        # 一共要爬取的页数
        news_num_per_page = min(self.toutiao_each_page_num, news_num)
        pages_num = int(news_num / news_num_per_page)
        for i in range(pages_num * 2):
            page_url = self.toutiao_news_roll_url.format(now_time, now_time)
            try:
                # 设置headers,读取第i+1页的新闻数据
                page = self.get_response('https://www.toutiao.com/ch/news_society/', page_url)
                page = page[page.index('{'):page.rindex('}') + 1]
                # 转为json格式
                jd = json.loads(page)
                now_time = jd['next']['max_behot_time']
            except Exception as e:
                logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                now_time -= random.randint(0, 3600)
                continue
            logger.info('Crawling Roll Success: {}.'.format(page_url))
            for news in jd['data']:
                '''
                #获取新闻信息：source_id,url,title,keywords,meida_name,abstract,time,news_content,review_num
                '''
                # source_id,url,title,keywords,media_name,abstract
                # time、news_content、review_num到新闻正文页获取
                # ext2="sh:comos-fynffnz3077632:0"
                # 提取出comos-fynffnz3077632与相关新闻id格式保持一致
                if news['is_feed_ad']:
                    continue
                news_obj = entities.news.NewsPlain()
                try:
                    news_obj.source_id = 'a'+news['group_id']
                    if datasources.get_db().find_news_by_source_id(session, source_id=news_obj.source_id):
                        continue
                    news_obj.url = 'https://www.toutiao.com/' + news_obj.source_id
                    news_obj.title = news['title']
                    news_obj.keywords = ','.join(news['label'])
                    news_obj.media_name = news['source']
                    if news_obj.media_name == '悟空问答':
                        continue
                    news_obj.abstract = news['abstract']
                    news_obj.review_num = int(news['comments_count'])
                    news_obj.source = news_obj.SourceEnum.toutiao

                    # 设置headers
                    # 获取新闻正文页html,提取news_content
                    news_html = self.get_response(page_url, news_obj.url)
                    news_html = news_html[news_html.index('articleInfo:'):news_html.rindex('commentInfo')]
                    news_html = news_html[news_html.index('{'):news_html.rindex('}') + 1]
                    dj = demjson.decode(news_html)
                    soup = bs4.BeautifulSoup(dj['content'], 'html.parser').text
                    soup = bs4.BeautifulSoup(soup, 'html.parser')
                    # ‘#’查找id名，‘.’查找class名
                    news_obj.time = datetime.datetime.strptime(dj['subInfo']['time'], "%Y-%m-%d %H:%M:%S")
                    news_obj.content = '\n'.join([p.text for p in soup.select('p')])
                    group_id = dj['groupId']
                    item_id = dj['itemId']
                    logger.info("Crawling Content Success: {}".format(news_obj.url))
                except Exception as e:
                    logger.warning("Crawling Content Failed: {}".format(news_obj.url))
                    continue

                review_url = self.toutiao_review_roll_url.format(group_id, item_id)
                try:
                    '''
                    #获取评论信息：user_id,user_name,area,review_content,time,agree
                    '''
                    # self.review_num是真实的评论数量，可作为热度的参考值。
                    # 但是评论内容最多取100条
                    review_page = self.get_response('https://www.toutiao.com/a{}/'.format(group_id), review_url)
                    jd = json.loads(review_page)
                    news_obj.review_num = jd['data']['total']
                    for review in jd['data']['comments']:
                        review_obj = entities.review.ReviewPlain()
                        review_obj.user_id = review['user']['user_id']
                        review_obj.user_name = review['user']['name']
                        review_obj.content = review['text']
                        seconds = float(review['create_time'])
                        review_obj.time = datetime.datetime.fromtimestamp(seconds)
                        review_obj.agree = review['digg_count']
                        news_obj.reviews.append(review_obj)
                    logger.info("Crawling Review Page Success: {}".format(review_url))
                except Exception as e:
                    # 评论出错直接忽略
                    logger.warning("Crawling Review Page Failed: {}".format(review_url))
                utils.utils.remove_wild_char_in_news(news_obj)
                datasources.get_db().upsert_news_or_news_list(session, news_obj, commit_now=False)
                news_count += 1
                if news_count >= news_num:
                    break
            if news_count >= news_num:
                break
        datasources.get_db().commit_session(session)
        datasources.get_db().close_session(session)
