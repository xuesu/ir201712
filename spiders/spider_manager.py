# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import threading

import my_exceptions.base_exception
import spiders.ifeng_spider
import spiders.sina_spider
import spiders.tencent_spider
import spiders.toutiao_spider
import utils.decorator


@utils.decorator.Singleton
class SpiderManager(object):
    def __init__(self):
        self.spiders = {
            "sina": spiders.sina_spider.SinaSpider(),
            "tencent": spiders.tencent_spider.TencentSpider(),
            "toutiao": spiders.toutiao_spider.ToutiaoSpider(),
            "ifeng": spiders.ifeng_spider.IFengSpider()
        }

    def crawl(self, num=None, numbers=None):
        """
        :param num: number of news to crawl. If num is set and numbers is None, method will dispatch 4/num to each spider.
        :param numbers: list or dict, e.g:{"sina", 2000} or [2000]
        :return:
        """
        if numbers is not None:
            if isinstance(numbers, list):
                numbers = {k: v for k, v in zip(self.spiders.keys(), numbers)}
        elif num is not None:
            numbers = {k: int(num / len(self.spiders)) for k in self.spiders.keys()}
        if numbers is None:
            raise my_exceptions.base_exception.RequriedParameterEmpty("SpiderManager.crawl", "numbers")
        if not isinstance(numbers, dict):
            raise my_exceptions.base_exception.InvalidParameterIRException("SpiderManager.crawl", "numbers", dict, numbers)

        ths = []
        for spider_name in self.spiders:
            spider = self.spiders[spider_name]
            num = numbers.get(spider_name, 0)
            th = threading.Thread(target=spider.get_news, kwargs={"news_num": num})
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
