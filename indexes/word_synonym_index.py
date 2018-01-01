import os

import pyspark.mllib.feature

import config
import datasources
import py4j.protocol
import update.segment


class WordSynonymIndex(object):
    def __init__(self):
        self.inited = False
        self.model = None

    def init(self, force_refresh=False):
        if self.inited:
            return
        if force_refresh or not os.path.exists(config.indexes_config.word_synonym_model_cache_path):
            self.build()
        else:
            self.model = pyspark.mllib.feature.Word2VecModel.load(
                config.get_spark_context(),
                config.indexes_config.word_synonym_model_cache_path)
        self.inited = True

    def build(self, text_df=None):
        if text_df is None:
            sqlsession = datasources.get_db().create_session()
            sparksession = pyspark.sql.SparkSession(config.get_spark_context())
            text_df = sparksession.createDataFrame(
                datasources.get_db().find_news_plain_text(sqlsession))
            datasources.get_db().close_session(sqlsession)

        train_data = update.segment.cut4synonym_index(text_df)
        word2vec = pyspark.mllib.feature.Word2Vec()
        self.model = word2vec.fit(train_data)
        self.model.save(config.get_spark_context(),
                        config.indexes_config.word_synonym_model_cache_path)

    def collect(self, word_text, num=None):
        """
        Attention: only search in local!
        :param word_text:
        :param num:
        :return:
        """
        if num is None:
            num = config.indexes_config.word_synonym_default_number
        try:
            ans = self.model.findSynonyms(word_text, num)
            ans = [a[0] for a in ans]
            ans.append(word_text)
            return ans
        except py4j.protocol.Py4JJavaError:
            return None
