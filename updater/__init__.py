# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import pyspark

import config
import datasources
import spiders.spider_manager
import updater.segment
import utils.decorator


@utils.decorator.Singleton
class Updater(object):
    """
    use to manage crawl, create & update index/database.
    """

    def __init__(self):
        pass

    def crawl(self, num=None, numbers=None):
        spiders.spider_manager.SpiderManager().crawl(num, numbers)

    def segment(self):
        sqlsession = datasources.get_db().create_session()
        sparksession = pyspark.sql.SparkSession(config.get_spark_context())
        text_df = sparksession.createDataFrame(datasources.get_db().find_news_plain_text(sqlsession))
        updater.segment.cut4db(text_df)

    def update_statistics(self):
        avg_word_num = 0
        news_num = 0
        sqlsession = datasources.get_db().create_session()
        for news in datasources.get_db().find_news_list(sqlsession):
            news.word_num = len(news.posting_list)
            avg_word_num += news.word_num
            news_num += 1
            datasources.get_db().upsert_news_or_news_list(sqlsession, news, commit_now=False)
        datasources.get_db().commit_session(sqlsession)
        avg_word_num /= news_num
        wordset = dict()
        for word in datasources.get_db().find_word_list(sqlsession):
            if word.text not in wordset:
                wordset[word.text] = list()
            wordset[word.text].append(word)
        for word_text in wordset:
            if len(wordset[word_text]) > 1:
                news_ids = set()
                word_merged = wordset[word_text][0]
                for word in wordset[word_text][1:]:
                    word_merged.cf += word.cf
                    word_merged.df += word.df
                    for posting in word_merged.posting_list:
                        if posting.news_id in news_ids:
                            continue
                        else:
                            news_ids.add(posting.news_id)
                        posting.word_id = word_merged.id
                        word_merged.posting_list.append(posting)
                    datasources.get_db().delete_word(sqlsession, word, commit_now=False)
                datasources.get_db().upsert_word_or_word_list(sqlsession, word_merged, commit_now=False)
        datasources.get_db().commit_session(sqlsession)
        datasources.get_db().close_session(sqlsession)

    def prepossess(self):
        self.segment()
        self.update_statistics()

    def update(self, num=20):
        self.crawl(num)
        self.prepossess()
