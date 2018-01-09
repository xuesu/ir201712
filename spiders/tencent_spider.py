# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import bs4
import datetime
import simplejson as json
import itertools
import random

import datasources
import entities.news
import entities.review
import logs.loggers
import spiders.base_spider
import utils.utils

logger = logs.loggers.LoggersHolder().get_logger("spiders")


class TencentSpider(spiders.base_spider.BaseSpider):
    def __init__(self):
        super(TencentSpider, self).__init__()
        # 腾讯新闻翻页地址,date=2016-11-29,page=1,2,3……
        self.tencent_news_roll_url = r'http://roll.news.qq.com/interface/roll.php?%.16f&cata=newssh&site=news&date={}&page={}&mode=1&of=json'
        # 翻页地址Header.Referer,date=2016-11-29
        self.tencent_roll_referer = r'http://roll.news.qq.com/index.htm?site=news&mod=1&date={}&cata=newssh'
        # 一页的新闻数,不能修改
        self.tencent_each_page_num = 50
        # 评论翻页地址,review_id,orinum取评论数（最大取100）,orirepnum回复数目，默认2
        self.tencent_review_roll_url = r'http://coral.qq.com/article/{}/comment/v2?callback=jQuery1124020207774121939615_1511705939893&orinum=100&oriorder=o&pageflag=1&cursor=0&scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=1&_=1511705939894'

    def get_news(self, news_num):
        session = datasources.get_db().create_session()
        news_count = 0
        for delta_day in range(news_num):
            date = utils.utils.get_date_before(delta_day)
            # 每天最多三页新闻：3*50
            for page_index in range(1):
                page_url = (self.tencent_news_roll_url % random.random()).format(date, page_index + 1)
                try:
                    # 设置headers,读取第i+1页的新闻数据
                    page = self.get_response(referer=self.tencent_roll_referer.format(date),
                                             url=page_url, encoding='gbk')
                    # 转为json格式
                    jd = json.loads(page)
                except Exception as e:
                    logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                    continue
                if str(jd['response']['code']) != '0':
                    break
                # 得到一页html格式的50条新闻
                page_html = jd['data']['article_info']
                try:
                    page_bs = bs4.BeautifulSoup(page_html, 'html.parser')
                except Exception as e:
                    logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                    continue
                # ‘#’查找id名，‘.’查找class名 , 直接查找标签名
                for news in page_bs.select('li'):
                    '''
                    #获取新闻信息：url,title,time
                    '''
                    news_obj = entities.news.NewsPlain()
                    timestr = date[:4] + '-' + news.span.text
                    if timestr.index(' ') == len(timestr) - 5:
                        timestr = timestr[:timestr.index(' ') + 1] + '0' + timestr[timestr.index(' ') + 1:]
                    try:
                        news_obj.time = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M")
                    except Exception as e:
                        logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                        continue
                    news_obj.url = news.a['href']
                    if datasources.get_db().find_news_by_url(session, news_obj.url):
                        continue
                    news_obj.title = news.a.text
                    news_obj.source = news_obj.SourceEnum.tencent
                    try:
                        # 设置headers
                        # 获取新闻正文页html
                        news_html = self.get_response(referer='', url=news_obj.url, encoding='gbk')
                        soup = bs4.BeautifulSoup(news_html, 'html.parser')
                        # ‘#’查找id名，‘.’查找class名
                        news_obj.media_name = soup.select('.a_source')[0].text
                        news_obj.content = '\n'.join([p.text for p in soup.select('#Cnt-Main-Article-QQ')[0].select('p')])
                        news_obj.abstract = news_obj.content[:100]
                        review_info = str(soup)
                        idx = review_info.index('cmt_id')
                        review_info = review_info[idx + 9:idx + 19]
                        # review_info just like 'cmt_id= 111111;'
                        review_page_id = review_info.strip()
                        new_info = str(soup.html.head.find_next(name='script', attrs={'type': 'text/javascript'}))
                        id_str = new_info.split('\n')[6]
                        # keywords_str just like tags:['a','b','c'],
                        keywords_str = new_info.split('\n')[11]
                        news_obj.keywords = keywords_str[keywords_str.index('[') + 1:keywords_str.rindex(']')]
                        news_obj.keywords = news_obj.keywords.replace('\'', '')
                    except Exception as e:
                        # set default
                        logger.warning("Crawling Content Failed: {}".format(news_obj.url))
                        continue
                    logger.info("Crawling Content Success: {}".format(news_obj.url))
                    # 若爬取评论失败，则为0
                    news_obj.review_num = 0
                    if review_page_id:
                        try:
                            review_url = self.tencent_review_roll_url.format(review_page_id)
                            logger.info("Crawling Review Page Success: {}".format(review_url))
                        except Exception as e:
                            logger.warning("Crawling Review Page Failed: {}".format(review_url))
                        try:
                            review_page = self.get_response(
                                referer='http://page.coral.qq.com/coralpage/comment/news.html',
                                url=review_url, encoding='gbk')
                            jd = json.loads(review_page[review_page.index('{'):review_page.rindex('}') + 1])
                            news_obj.review_num = jd['data']['oritotal']
                            # 原始评论
                            comm_list = itertools.chain(jd['data']['oriCommList'], *jd['data']['repCommList'])
                            for review in comm_list:
                                review_obj = entities.review.ReviewPlain()
                                review_obj.user_id = review['userid']
                                review_obj.content = review['content']
                                seconds = int(review['time'])
                                review_obj.time = datetime.datetime.fromtimestamp(seconds)
                                review_obj.agree = int(review['up'])
                                user_info = jd['data']['userList'][review_obj.user_id]
                                review_obj.user_name = user_info['nick']
                                review_obj.area = user_info['region']
                                if review_obj.area is not None:
                                    review_obj.area = review_obj.area[-19:]
                                news_obj.reviews.append(review_obj)
                        except Exception as e:  # 评论出错直接忽略
                            logger.warning("An invalid comment.")
                    utils.utils.remove_wild_char_in_news(news_obj)
                    datasources.get_db().upsert_news_or_news_list(session, news_obj, commit_now=False)
                    news_count += 1
                    if news_count >= news_num:
                        break
                if news_count >= news_num:
                    break
            if news_count >= news_num:
                break
        datasources.get_db().commit_session(session)
        datasources.get_db().close_session(session)
