# -*- coding:utf-8 -*-
"""
@author: xidongbo

"""
import pyspark

import config
import datasources
import spiders.spider_manager
import update.segment
import utils.decorator


@utils.decorator.Singleton
class Updater(object):
    """
    use to manage crawl, create & update index/database.
    """

    def __init__(self):
        self.sqlsession = None
        self.sparksession = None

    def crawl(self, num=None, numbers=None):
        spiders.spider_manager.SpiderManager().crawl(num, numbers)

    def segment(self):
        text_df = self.sparksession.createDataFrame(datasources.get_db().find_news_plain_text(self.sqlsession))
        update.segment.cut4db(text_df)

    def update_statistics(self):
        avg_word_num = 0
        news_num = 0
        for news in datasources.get_db().find_news_list(self.sqlsession):
            news.word_num = len(news.posting_list)
            avg_word_num += news.word_num
            news_num += 1
            datasources.get_db().upsert_news_or_news_list(self.sqlsession, news, commit_now=False)
        datasources.get_db().commit_session(self.sqlsession)
        avg_word_num /= news_num
        wordset = dict()
        for word in datasources.get_db().find_word_list(self.sqlsession):
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
                    datasources.get_db().delete_word(self.sqlsession, word, commit_now=False)
                datasources.get_db().upsert_word_or_word_list(self.sqlsession, word_merged, commit_now=False)
        datasources.get_db().commit_session(self.sqlsession)

    def prepossess(self):
        self.segment()
        self.update_statistics()

    def update(self, num=20):
        self.sqlsession = datasources.get_db().create_session()
        self.sparksession = pyspark.sql.SparkSession(config.get_spark_context())
        self.crawl(num)
        self.prepossess()
        datasources.get_db().close_session(self.sqlsession)
        self.sqlsession = None
        self.sparksession = None


if __name__ == '__main__':
    updater = Updater()
    updater.update(100)
