# -*- coding:utf-8 -*-
"""
@author: xuesu
"""
import jieba.posseg

import datasources.datasource
import utils.decorator


class TextExtractor(object):
    def __init__(self):
        self.datasource = datasources.datasource.DataSourceHolder()

    @staticmethod
    def tokenize(unicode_sentence, mode="default", HMM=True):
        """
        Tokenize a sentence and yields tuples of (word, start, end)

        Parameter:
            - sentence: the str(unicode) to be segmented.
            - mode: "default" or "search", "search" is for finer segmentation.
            - HMM: whether to use the Hidden Markov Model.
        """
        start = 0
        if mode == 'default':
            for w, pos in jieba.posseg.cut(unicode_sentence, HMM=HMM):
                width = len(w)
                yield (w, pos, start, start + width)
                start += width
        else:
            for w, pos in jieba.posseg.cut(unicode_sentence, HMM=HMM):
                width = len(w)
                if len(w) > 2:
                    for i in range(len(w) - 1):
                        gram2 = w[i:i + 2]
                        if jieba.posseg.dt.FREQ.get(gram2):
                            yield (gram2, start + i, start + i + 2)
                if len(w) > 3:
                    for i in range(len(w) - 2):
                        gram3 = w[i:i + 3]
                        if jieba.posseg.dt.FREQ.get(gram3):
                            yield (gram3, start + i, start + i + 3)
                yield (w, pos, start, start + width)
                start += width

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
        wordset = dict()
        for word in self.datasource.find_word_list(sqlsession):
            if word.text not in wordset:
                wordset[word.text] = list()
            wordset[word.text].append(word)
        for word_text in wordset:
            if len(wordset[word_text]) > 1:
                for word in wordset[word_text]:
                    print(word.text, word.cf, word.df, word.posting_list)
                word_merged = wordset[word_text][0]
                for word in wordset[word_text][1:]:
                    word_merged.cf += word.cf
                    word_merged.df += word.df
                    word_merged.posting_list += word.posting_list
                    self.datasource.delete_word(sqlsession, word)
                self.datasource.upsert_word(sqlsession, word_merged)
        self.datasource.close_mysql_session(sqlsession)

    @utils.decorator.timer
    def recut(self, text_df):

        def segment_map(r):
            words = dict()
            title_words = [(w[0], w[1], w[2]) for w in TextExtractor.tokenize(r.title)]
            for word, pos_tag, position in title_words:
                word_key = '%s\t%s' % (word, pos_tag)
                if word not in words:
                    words[word_key] = {"title": [], "content": [], "news_id": r.id}
                words[word_key]["title"].append(position)
            content_words = [(w[0], w[1], w[2]) for w in TextExtractor.tokenize(r.content)]
            for word, pos_tag, position in content_words:
                word_key = '%s\t%s' % (word, pos_tag)
                if word not in words:
                    words[word_key] = {"title": [], "content": [], "news_id": r.id}
                words[word_key]["content"].append(position)
            return [(k, words[k]) for k in words.keys()]

        @utils.decorator.run_executor_node
        @utils.decorator.timer
        def saving_foreachPartition(rdd):
            import datasources.datasource
            import entities.words
            datasource = datasources.datasource.DataSourceHolder()
            session = datasource.create_mysql_session()
            word_list = []
            for text, pitr in rdd:
                word_text = text[: text.rindex('\t')]
                pos = text[text.rindex('\t') + 1:]
                posting_list = []
                word = entities.words.Word(text=word_text, df=0, cf=0, pos=pos)
                for posting_j in pitr:
                    tf = len(posting_j["title"]) + len(posting_j["content"])
                    word.cf += tf
                    word.df += 1
                    word_posting = entities.words.WordPosting(news_id=posting_j["news_id"],
                                                              title_positions=posting_j["title"],
                                                              content_positions=posting_j["content"], tf=tf)
                    posting_list.append(word_posting)
                word.posting_list = posting_list
                word_list.append(word)
            datasource.upsert_word(session, word_list)
            datasource.close_mysql_session(session)

        rdd = text_df.rdd.flatMap(segment_map).groupByKey()
        rdd.foreachPartition(saving_foreachPartition)
        self.update_statistics()
