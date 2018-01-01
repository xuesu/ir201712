import itertools
import operator
import os
import pyspark.mllib.feature
import pyspark.storagelevel
import shutil
import math

import config
import datasources
import update.segment
import utils.decorator
import utils.utils


class WordCoOccurrenceIndex(object):
    def __init__(self):
        self.inited = False
        self.model = None

    def init(self, force_refresh=False):
        if self.inited:
            return
        if force_refresh or not os.path.exists(config.indexes_config.word_cooccurrence_model_cache_path):
            self.build()
        else:
            self.model = config.get_spark_context().pickleFile(config.indexes_config.word_cooccurrence_model_cache_path)
        self.model.persist(storageLevel=pyspark.storagelevel.StorageLevel.MEMORY_AND_DISK)
        self.inited = True

    @utils.decorator.timer
    def build(self, text_df=None):

        @utils.decorator.run_executor_node
        def build_foreach(r):
            r = set(r)
            for c in itertools.combinations(r, 2):
                yield (utils.utils.merge_two_str(*c), 1)

        if text_df is None:
            sqlsession = datasources.get_db().create_session()
            sparksession = pyspark.sql.SparkSession(config.get_spark_context())
            text_df = sparksession.createDataFrame(
                datasources.get_db().find_news_plain_text(sqlsession))
            datasources.get_db().close_session(sqlsession)

        train_data = update.segment.cut4cooccurrence_index(text_df)
        self.model = train_data.flatMap(build_foreach).reduceByKey(operator.add).mapValues(
            lambda x: math.log(x + 1)).sortByKey()
        if os.path.exists(config.indexes_config.word_cooccurrence_model_cache_path):
            shutil.rmtree(config.indexes_config.word_cooccurrence_model_cache_path)
        self.model.saveAsPickleFile(config.indexes_config.word_cooccurrence_model_cache_path)
        self.inited = True

    @utils.decorator.timer
    def collect(self, word_text_list):
        """
        Attention: only search in local!
        :param word_text_list:
        :param num:
        :return:
        """
        self.check_init()
        word_text_list = set(word_text_list)
        return sum(sum(self.model.lookup(utils.utils.merge_two_str(*c))) for c in itertools.combinations(word_text_list, 2))
