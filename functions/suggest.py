import config.config_manager
import indexes.index_holder
import sorter.sorter_holder
import utils.utils

function_config = config.config_manager.ConfigManager().functions_config


def suggest_autocomplete(search_text):
    search_text = utils.utils.remove_wild_char(search_text)
    words_regex_list = search_text.split(' ')
    candidates = indexes.index_holder.IndexHolder().word_index.collect(words_regex_list[-1])
    candidates = sorter.sorter_holder.SorterHolder().word_suggest_sorter.mysort(candidates)[
                 :function_config.suggest_num]
    return [word.text for word in candidates]
