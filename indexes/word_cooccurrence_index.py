import itertools
import os
import pickle
import math

import config
import datasources
import indexes
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
                self.model = pickle.load(fin)

    @utils.decorator.timer
    def build(self):

        @utils.decorator.run_executor_node
        def build_map(news_texts, length):
            import update.segment
            ans = []
            word_texts = [token[0] for token in update.segment.tokenize_filter_stop(news_texts[1])]
            word_texts = [text for text in set(word_texts)]
            word_texts.sort()
            ans += itertools.combinations(word_texts, 2)
            que = {}
            tokens = [(token[0], token[3]) for token in update.segment.tokenize_filter_stop(news_texts[2])]
            e = 0
            for s in range(len(tokens)):
                while e < len(tokens) and tokens[e][1] < tokens[s][1] + length:
                    que[tokens[e][0]] = que.get(tokens[e][0], 0) + 1
                    e += 1
                for text2 in que:
                    if text2 < tokens[s][0]:
                        ans.append((text2, tokens[s][0]))
                    elif text2 > tokens[s][0]:
                        ans.append((tokens[s][0], text2))
                if que[tokens[s][0]] > 1:
                    que[tokens[s][0]] -= 1
                else:
                    que.pop(tokens[s][0])
                s += 1
            return ans

        sqlsession = datasources.get_db().create_session()
        texts = datasources.get_db().find_news_plain_text(sqlsession)
        part_num = (len(texts) + 99) // 100
        train_data = config.get_spark_context().parallelize(texts, part_num)
        del texts

        def merge_d_x(d, x):
            d[x] = d.get(x, 0) + 1
            return d

        def merge_d_d(d, d2):
            for x in d2:
                d[x] = d.get(x, 0) + d2[x]
            return d

        def reduce_d(d, length):
            l = [(d[k], k) for k in d]
            l.sort(reverse=True)
            d = {k: math.log(v + 1) for v, k in l[:length]}
            return d

        self.model = {k:v for k, v in train_data.flatMap(
            lambda data: build_map(data, config.indexes_config.word_cooccurrence_model_window_length))\
            .combineByKey(lambda x: {x: 1}, merge_d_x, merge_d_d)\
            .mapValues(lambda d: reduce_d(d, config.indexes_config.word_cooccurrence_model_memo_length)).collect()}
        datasources.get_db().close_session(sqlsession)
        if os.path.exists(config.indexes_config.word_cooccurrence_model_cache_path):
            os.remove(config.indexes_config.word_cooccurrence_model_cache_path)
        with open(config.indexes_config.word_cooccurrence_model_cache_path, 'wb') as fout:
            pickle.dump(self.model, fout)

    def collect(self, word_text_list):
        """
        :param word_id_list:
        :param num:
        :return:
        """
        word_text_list = set(word_text_list)
        word_text_list = [word_text for word_text in word_text_list]
        word_text_list.sort()
        ans = 0
        for i, text in enumerate(word_text_list):
            ans += sum([self.model.get(text, {}).get(text2, 0) for text2 in word_text_list[i + 1:]])
        return ans
