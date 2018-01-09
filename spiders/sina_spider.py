# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import bs4
import datetime
import simplejson as json

import datasources
import entities.news
import entities.review
import logs.loggers
import spiders.base_spider
import utils.utils

logger = logs.loggers.LoggersHolder().get_logger("spiders")


class SinaSpider(spiders.base_spider.BaseSpider):
    def __init__(self):
        super(SinaSpider, self).__init__()
        # 新浪新闻翻页地址,show_num=22,page=1,2,3……
        self.sina_news_roll_url = r'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=shxw&cat_2==zqsk||=qwys||=shwx||=fz-shyf&level==1||=2&show_ext=1&show_all=1&show_num={}&tag=1&format=json&page={}&callback=newsloadercallback&_=1509122181439'
        # 相关新闻翻页地址,pageurl=url,offset=0,5,10……
        self.sina_related_news_roll_url = r'http://cre.mix.sina.com.cn/api/v3/get?rfunc=103&fields=url&feed_fmt=1&cateid=1o_1r&cre=newspagepc&mod=f&merge=3&statics=1&this_page=1&dedup=32&pageurl={}&offset={}&length=5&lid=-2000&callback=feedCardJsonpCallback&_=1509184623811'
        # 新浪评论翻页地址,page_size取评论数（最大取100）
        self.sina_review_roll_url = r'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=sh&newsid={}&group=0&compress=0&ie=utf-8&oe=utf-8&page=1&page_size={}&jsvar=loader_1509195624657_56915173'
        # 每条新闻爬取的最大评论数
        self.max_reviews_num = 200
        # 一页的新闻数
        self.sina_each_page_num = 22

    def get_news(self, news_num):
        session = datasources.get_db().create_session()
        news_count = 0
        news_num_per_page = min(self.sina_each_page_num, news_num)
        for i in range(news_num):
            page_url = self.sina_news_roll_url.format(news_num_per_page, i + 1)
            try:
                # 设置headers,读取第i+1页的新闻数据
                page = self.get_response('http://news.sina.com.cn/society/', page_url)
                page = page[page.index('{'):page.rindex('}') + 1]
                # 转为json格式
                jd = json.loads(page)
            except Exception as e:
                logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                continue
            logger.info('Crawling Roll Success: {}.'.format(page_url))
            for news in jd['result']['data']:
                news_obj = entities.news.NewsPlain()
                try:
                    source_id = news['ext2'].split(':')[1]
                    news_obj.url = news['url']
                    if datasources.get_db().find_news_by_url(session, news_obj.url):
                        continue
                    news_obj.title = news['title']
                    news_obj.keywords = news['keywords']
                    news_obj.media_name = news['media_name']
                    news_obj.abstract = news['ext5']
                    news_obj.source = news_obj.SourceEnum.sina
                    seconds = float(news['createtime'])
                    news_obj.time = datetime.datetime.fromtimestamp(seconds)
                    # 设置headers
                    # 获取新闻正文页html,提取news_content
                    self.headers[
                        'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    news_html = self.get_response(page_url, news_obj.url)
                    soup = bs4.BeautifulSoup(news_html, 'html.parser')
                    # set default
                    self.headers['Accept'] = '*/*'
                    # ‘#’查找id名，‘.’查找class名
                    news_obj.content = '\n'.join([p.text for p in soup.select('#article')[0].select('p')])
                    logger.info("Crawling Content Success: {}".format(news_obj.url))
                except Exception as e:
                    # set default
                    self.headers['Accept'] = '*/*'
                    logger.warning("Crawling Content Failed: {}".format(news_obj.url))
                    continue
                news_obj.review_num = 0
                review_url = self.sina_review_roll_url.format(source_id, self.max_reviews_num)
                try:
                    '''
                    #获取评论信息：user_id,user_name,area,review_content,time,agree
                    '''
                    # self.review_num是真实的评论数量，可作为热度的参考值。
                    # 但是评论内容最多取100条
                    review_page = self.get_response(news_obj.url, review_url)
                    jd = json.loads(review_page[review_page.index('{'):review_page.rindex('}') + 1])
                    news_obj.review_num = jd['result']['count']['show']
                    for review in jd['result']['cmntlist']:
                        review_obj = entities.review.ReviewPlain()
                        review_obj.user_id = review['uid']
                        review_obj.user_name = review['nick']
                        review_obj.area = review['area']
                        review_obj.content = review['content']
                        review_obj.time = review['time']
                        review_obj.agree = review['agree']
                        news_obj.reviews.append(review_obj)
                    logger.info("Crawling Review Page Success: {}".format(review_url))
                except Exception as e:
                    # 评论出错直接忽略
                    logger.warning("Crawling Review Page Failed: {}".format(review_url))
                utils.utils.remove_wild_char_in_news(news_obj)
                datasources.get_db().upsert_news_or_news_list(session, news_obj)
                news_count += 1
                if news_count >= news_num:
                    break
            if news_count >= news_num:
                break
        datasources.get_db().commit_session(session)
        datasources.get_db().close_session(session)
