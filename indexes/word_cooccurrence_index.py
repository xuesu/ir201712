import itertools
import operator
import os
import pickle
import math

import config
import datasources
import update.segment
import utils.decorator
import utils.utils


class WordCoOccurrenceIndex(object):
    def __init__(self):
        self.model = None

    def init(self, force_refresh=False):
        if force_refresh or not os.path.exists(config.indexes_config.word_cooccurrence_model_cache_path):
            self.build()
        else:
            with open(config.indexes_config.word_cooccurrence_model_cache_path, 'rb') as fin:
                pickle.load(self.model, fin)

    @utils.decorator.timer
    def build(self):

        @utils.decorator.run_executor_node
        def build_mapPartition(data, length):
            import datasources
            import update.segment
            session = datasources.get_db().create_session()
            ans = []
            que = []
            for news_texts in data:
                for token in update.segment.tokenize(news_texts[1]):
                    text = token[0]
                    pos = token[1]
                    word_id = datasources.get_db().find_word_id_by_text(text)
                    if word_id is None:
                        continue
                    while que and que[0][3] < token[3] - length:
                        que = que[1:]
                    for word_id2, _ in que:
                        if word_id < word_id2:
                            ans.append((word_id, word_id2))
                        else:
                            ans.append((word_id, word_id2))
                    que.append((word_id, pos))
            datasources.get_db().close_session(session)
            return ans

        sqlsession = datasources.get_db().create_session()
        train_data = config.get_spark_context().parallelize(datasources.get_db().find_news_plain_text(sqlsession))
        datasources.get_db().close_session(sqlsession)

        def merge_d_x(d, x):
            d[x] = d.get(x, 0) + 1
            return d

        def merge_d_d(d, d2):
            for x in d2:
                d[x] = d.get(x) + d2[x]
            return d

        def log_to_list(d):
            v = [(x, math.log(d[x])) for x in d]
            del d
            v.sort(key=lambda x: x[1], reverse=True)
            return v

        self.model = train_data.mapPartition(
            lambda data: build_mapPartition(data, config.indexes_config.word_cooccurrence_model_window_length))\
            .combineByKey(lambda x: {x: 1}, merge_d_x, merge_d_d).mapValues(log_to_list).collect()
        if os.path.exists(config.indexes_config.word_cooccurrence_model_cache_path):
            os.remove(config.indexes_config.word_cooccurrence_model_cache_path)
        with open(config.indexes_config.word_cooccurrence_model_cache_path, 'wb') as fout:
            pickle.dump(self.model, fout)

    def get_score(self, wid, other_wids):
        if wid not in self.model:
            return 0
        for wid2, score in self.model[wid]:
            if wid2 in other_wids:
                return score

    @utils.decorator.timer
    def collect(self, word_id_list):
        """
        :param word_id_list:
        :param num:
        :return:
        """
        word_id_list = set(word_id_list)
        return sum([self.get_score(wid, word_id_list) for wid in word_id_list])
