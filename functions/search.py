import utils.utils
import indexes.index_holder


def search(search_text):
    text = utils.utils.remove_wild_char(search_text)
    index_holder = indexes.index_holder.IndexHolder()
    words_regex_list = text.split(' ')
    words_info = [index_holder.word_index.find(word_regex) for word_regex in words_regex_list]
    