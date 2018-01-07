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


class IFengSpider(spiders.base_spider.BaseSpider):
    def __init__(self):
        super(IFengSpider, self).__init__()
        self.fenghuang_news_roll_url = r'http://news.ifeng.com/listpage/7837/{}/{}/rtlist.shtml'
        # docURL:sub_11111
        self.fenghuang_review_roll_url = r'http://comment.ifeng.com/get.php?callback=newCommentListCallBack&orderby=&docUrl={}&format=js&job=1&p=1&pageSize=20&callback=newCommentListCallBack&skey=e0d9fe'
        self.fenghuang_num = 50000
        self.fenghuang_each_page_num = 60

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
        day_num = (news_num + self.fenghuang_each_page_num - 1) // self.fenghuang_each_page_num * 2
        for delta_day in range(day_num):
            date = utils.utils.get_date_before(delta_day)
            # 每天最多三页新闻：3*50
            for page_index in range(1):
                page_url = self.fenghuang_news_roll_url.format(date, page_index + 1, self.fenghuang_each_page_num)
                try:
                    # 设置headers,读取第i+1页的新闻数据
                    page = self.get_response(referer='', url=page_url)
                except Exception as e:
                    logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                    continue
                try:
                    page_bs = bs4.BeautifulSoup(page, 'html.parser')
                except Exception as e:
                    logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                    continue
                # ‘#’查找id名，‘.’查找class名 , 直接查找标签名
                for news in page_bs.select('.newsList')[0].select('li'):
                    '''
                    #获取新闻信息：url,title,time
                    '''
                    news_obj = entities.news.NewsPlain()
                    timestr = date[:4] + '-' + news.h4.text
                    timestr = timestr.replace('/', '-')
                    if timestr.index(' ') == len(timestr) - 5:
                        timestr = timestr[:timestr.index(' ') + 1] + '0' + timestr[timestr.index(' ') + 1:]
                    try:
                        news_obj.time = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M")
                    except Exception as e:
                        logger.warning('Crawling Roll Failed: {}.'.format(page_url))
                        continue
                    news_obj.url = news.a['href']
                    news_obj.title = news.a.text
                    news_obj.source = news_obj.SourceEnum.ifeng
                    try:
                        # 设置headers
                        # 获取新闻正文页html
                        news_html = self.get_response(referer='', url=news_obj.url)
                        soup = bs4.BeautifulSoup(news_html, 'html.parser')
                        # ‘#’查找id名，‘.’查找class名
                        news_obj.media_name = soup.select('.ss03')[0].a.text
                        news_obj.content = '\n'.join([p.text for p in soup.select('#artical_real')[0].select('p')])
                        news_obj.abstract = news_obj.content[:100]
                        review_info = news_html
                        idx = review_info.index('commentUrl')
                        review_info = review_info[idx + 13:]
                        review_page_id = review_info[:review_info.index(',') - 1]
                    except Exception as e:
                        # set default
                        logger.warning("Crawling Content Failed: {}".format(news_obj.url))
                        continue
                    logger.info("Crawling Content Success: {}".format(news_obj.url))
                    # 若爬取评论失败，则为0
                    news_obj.review_num = 0
                    if review_page_id:
                        try:
                            review_url = self.fenghuang_review_roll_url.format(review_page_id)
                            logger.info("Crawling Review Page Success: {}".format(review_url))
                        except Exception as e:
                            logger.warning("Crawling Review Page Failed: {}".format(review_url))
                        try:
                            review_page = self.get_response(
                                referer='http://page.coral.qq.com/coralpage/comment/news.html',
                                url=review_url)
                            review_page = review_page[review_page.index('='):]
                            left = review_page.index('{')
                            right = review_page.rindex('}', 0, len(review_page) - 10) + 1
                            review_page = review_page[left:right]
                            jd = json.loads(review_page)
                            news_obj.review_num = jd['count']
                            valid_vevs = [rev for rev in jd['comments']]
                            for rev in jd['comments']:
                                valid_vevs += rev['parent']
                            for review in valid_vevs:
                                review_obj = entities.review.ReviewPlain()
                                review_obj.user_id = review['user_id']
                                news_obj.source_id = review['article_id']
                                review_obj.content = review['comment_contents']
                                seconds = int(review['create_time'])
                                review_obj.time = datetime.datetime.fromtimestamp(seconds)
                                review_obj.agree = int(review['uptimes'])
                                review_obj.user_name = review['uname']
                                review_obj.area = review['ip_from']
                                news_obj.reviews.append(review_obj)
                        except Exception as e:  # 评论出错直接忽略
                            logger.warning("Handling an invalid comment Failed.")
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
