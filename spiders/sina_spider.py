# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import bs4
import copy
import datetime
import simplejson as json

import datasources.datasource
import entities.news
import entities.review
import logs.loggers
import spiders.base_spider
import utils.utils

logger = logs.loggers.LoggersHolder().get_logger("spiders")
datasource_holder = datasources.datasource.DataSourceHolder()


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

        # header['Host']和Header['Referer']根据需要添加
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
        }
        self.session = datasource_holder.create_mysql_session()

    def get_news(self, news_num):
        """
        '获取如下数据：
            '获取新闻数据：
                news_id:新闻id,
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
        news_count = 0
        # 一共要爬取的页数
        pages_num = int(news_num / self.sina_each_page_num)
        for i in range(pages_num * 2):
            logger.info('get %dth page news,each page %d news.' % (i + 1, self.sina_each_page_num))
            page_url = self.sina_news_roll_url.format(self.sina_each_page_num, i + 1)
            try:
                # 设置headers,读取第i+1页的新闻数据
                page = self.get_response('http://news.sina.com.cn/society/', page_url)
                page = page[page.index('{'):page.rindex('}') + 1]
                # 转为json格式
                jd = json.loads(page)
            except Exception as e:
                logger.warning('Failed: ' + page_url)
                continue
            for news in jd['result']['data']:
                '''
                #获取新闻信息：news_id,url,title,keywords,meida_name,abstract,time,news_content,review_num
                '''
                # 从字典拿到news_id,url,title,keywords,media_name,abstract
                # time、news_content、review_num到新闻正文页获取
                news_count += 1
                # ext2="sh:comos-fynffnz3077632:0"
                # 提取出comos-fynffnz3077632与相关新闻id格式保持一致
                news_obj = entities.news.NewsPlain()
                try:
                    news_obj.news_id = news['ext2'].split(':')[1]
                    if datasource_holder.find_news_by_id(self.session, news_id=news_obj.news_id):
                        continue
                    news_obj.url = news['url']
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
                '''
                #获取相关新闻id :  related_id
                '''
                news_obj.related_id = ''
                # 翻页获取related_id
                for offset in [0, 5, 10]:  # 0,5,10……
                    related_page_url = self.sina_related_news_roll_url.format(news_obj.url, offset)
                    try:
                        related_page = self.get_response(news_obj.url, related_page_url)
                        related_jd = json.loads(related_page[related_page.index('{'):related_page.rindex('}') + 1])
                        news_list = related_jd['result']['data']
                        if len(news_list) < 1:
                            break
                        for news in news_list:
                            # 只提取相关的文本新闻
                            if news['docid'][:5] != 'comos':
                                continue
                            news_obj.related_id += news['docid'].replace(':', '-') + ','
                            logger.info("Crawling Related Page Success: {}".format(related_page_url))
                    except Exception as e:
                        # 相关新闻出错直接忽略
                        logger.warning("Crawling Related Page Failed: {}".format(related_page_url))
                news_obj.related_id = news_obj.related_id[0:-1]
                news_obj.review_num = 0
                review_url = self.sina_review_roll_url.format(news_obj.news_id, self.max_reviews_num)
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
                        review_obj.news_id = news_obj.news_id
                        if review_obj.news_id == news_obj.news_id:
                            news_obj.reviews.append(review_obj)
                    logger.info("Crawling Review Page Success: {}".format(review_url))
                except Exception as e:
                    # 评论出错直接忽略
                    logger.warning("Crawling Review Page Failed: {}".format(review_url))
                utils.utils.remove_wild_char_in_news(news_obj)
                datasource_holder.upsert_news(self.session, news_obj)
            if news_count >= news_num:
                break

SinaSpider().get_news(30)
