# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import jieba

import datasources.datasource
import utils.decorator


class TextExtractor(object):
    def __init__(self):
        self.datasource = datasources.datasource.DataSourceHolder()

    def update_statistics(self):
        avg_word_num = 0
        news_num = 0
        sqlsession = self.datasource.create_mysql_session()
        for news in self.datasource.find_news_list(sqlsession):
            news.word_num = len(news.posting_list)
            avg_word_num += news.word_num
            news_num += 1
            self.datasource.upsert_news(sqlsession, news)
        avg_word_num /= news_num
        self.datasource.close_mysql_session(sqlsession)

    def recut(self, text_df):

        def segment_map(r):
            words = dict()
            title_words = [(w[0], w[1]) for w in jieba.tokenize(r.title)]
            for word, position in title_words:
                if word not in words:
                    words[word] = {"title": [], "content": [], "news_id": r.id}
                words[word]["title"].append(position)
            content_words = [(w[0], w[1]) for w in jieba.tokenize(r.content)]
            for word, position in content_words:
                if word not in words:
                    words[word] = {"title": [], "content": [], "news_id": r.id}
                words[word]["content"].append(position)
            return [(k, words[k]) for k in words.keys()]

        @utils.decorator.run_executor_node
        def saving_foreachPartition(rdd):
            import datasources.datasource
            import entities.words
            datasource = datasources.datasource.DataSourceHolder()
            session = datasource.create_mysql_session()
            for text, pitr in rdd:
                posting_list = []
                word = entities.words.Word(text=text, df=0)
                for posting_j in pitr:
                    tf = len(posting_j["title"]) + len(posting_j["content"])
                    word.cf += tf
                    word.df += 1
                    word_posting = entities.words.WordPosting(news_id=posting_j["news_id"],
                                                              title_positions=posting_j["title"],
                                                              content_positions=posting_j["content"], tf=tf)
                    posting_list.append(word_posting)
                word.posting_list = posting_list
                datasource.upsert_word(session, word)
            datasource.close_mysql_session(session)

        rdd = text_df.rdd.flatMap(segment_map).groupByKey()
        self.update_statistics()
        rdd.foreachPartition(saving_foreachPartition)
