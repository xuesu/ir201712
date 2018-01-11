import indexes
import utils.decorator
import utils.utils


class WordCoOccurrenceIndex(object):
    def __init__(self):
        self.model = None

    def init(self, force_refresh=False):
        pass

    @utils.decorator.timer
    def build(self):
        pass

    def collect(self, word_text_list):
        """
        :param word_id_list:
        :param num:
        :return:
        """
        word_text_list = set(word_text_list)
        posting_list = indexes.IndexHolder().posting_index.collect(word_text_list, 2)
        return sum([len([posting_list[k1][k2] for k2 in posting_list[k1]]) for k1 in posting_list])
