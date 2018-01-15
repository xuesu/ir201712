import utils.utils
import indexes
import functions.suggest
import config
import math
import datasources
import update.segment
import utils.decorator

RELEVENCE_RANKING = 1
TIME_DESCEND_RANKING = 2
TIME_INCREASE_RANKING = 3
HOT_RANKING = 4


def bm25(idf, tf, fl=1, avgfl=1, B=0.75, K1=1.2):

    return idf * ((tf * (K1 + 1)) / (tf + K1 * ((1 - B) + B * fl / avgfl)))


@utils.decorator.timer
def search(session, word_text_list, ranking):
    ans, df = indexes.IndexHolder().posting_index.collect(word_text_list, 2)  # the news at least contains 2 words
    print('ans', ans, 'df', df)
    ranking_set = list()
    if ranking == RELEVENCE_RANKING:
        document_counts = len(ans)
        for news_id, words_in_news in ans.items():
            bm25_score = 0
            for word, tf in words_in_news.items():
                idf = math.log(document_counts/(df[word] + 1)) + 1
                bm25_score += bm25(idf, tf[0])
            ranking_set.append((news_id, bm25_score))
    else:
        document_id_list = [news_id for news_id, v in ans.items()]
        r = datasources.get_db().find_news_time_and_review_num_by_id_list(session, document_id_list)
        if ranking == HOT_RANKING:
            ranking_set = [(u.id, u.review_num) for u in r]
        else:
            ranking_set = [(u.id, u.time) for u in r]

    if ranking == TIME_INCREASE_RANKING:
        ranking_set.sort(key=lambda k: k[1])
    else:
        ranking_set.sort(key=lambda k: k[1], reverse=True)
    return ranking_set


@utils.decorator.timer
def universal_search(session, search_text, ranking, page, num_in_page=10):
    # segment search_text. TODO
    word_regex_list = search_text.split(' ')
    word_regex_list = list(set(word_regex_list))
    try:
        # print(word_regex_list)
        word_regex_list.remove('')
    except ValueError:
        pass
    stop_nature_list = ['', 'w', 'x', 'y', 'c']
    word_processed_list = list()
    for u in word_regex_list:
        v = list()
        for w, pos, s, e in update.segment.tokenize(u):
            if pos == 'x' and w == '*':
                v.append(w)
            elif pos != 'x':
                if len(v) > 0 and v[-1].startswith('*'):
                    v[-1] += w
                elif pos not in stop_nature_list:
                    v.append(w)
        if len(v) > 0 and v[-1] == '*':
            if len(v) > 1:
                v[-2] += '*'
            else:
                v = []
        word_processed_list += v  # word_processed_list includes words segmented.
    fl = '*' in ''.join(word_processed_list)
    segment_word_4_search_list = list()
    word_regex_list = list()

    for u in word_processed_list:
        if '*' in u:
            word_regex_list.append(u)
        else:
            for v in update.segment.tokenize(u, mode='search'):
                if v[1] not in stop_nature_list:
                    segment_word_4_search_list.append(v[0])
    partial_similar_search_list = list()
    if fl:
        partial_similar_search_list = functions.suggest.suggest_similar_search(word_regex_list, 1)[0]
        try:
            partial_similar_search_list.remove('：')
        except ValueError:
            pass

    segment_word_4_search_list += partial_similar_search_list
    segment_word_4_search_list = list(set(segment_word_4_search_list))
    print('segment for search: ', segment_word_4_search_list)
    ranking_set = search(session, segment_word_4_search_list, ranking)
    # import pdb
    # pdb.set_trace()
    candidate_id_list = [u[0] for u in ranking_set[(page-1)*num_in_page: page*num_in_page]]
    if len(candidate_id_list) == 0:
        return 0, [], [' '.join(segment_word_4_search_list), partial_similar_search_list]
    result_list = [{'id': row.id,
                    'title': row.title,
                    'time': row.time} for row in datasources.get_db().find_news_title_and_time_by_id_list(session, candidate_id_list)]
    for r in result_list:
        for k, v in ranking_set[(page-1)*num_in_page: page*num_in_page]:
            if r.__contains__('score') is False and k == r['id']:
                r['score'] = v
                break
    result_list.sort(key=lambda r: r['score'], reverse=True if ranking != TIME_INCREASE_RANKING else False)
    return len(ranking_set), result_list, [' '.join(segment_word_4_search_list), partial_similar_search_list]

if __name__ == "__main__":
    config.spark_config.driver_mode = False
    config.spark_config.testing = True
    session = datasources.get_db().create_session()
    L, result_list, good_text = universal_search(session, "科学", 4, 1)
    print(L, result_list, good_text)
    datasources.get_db().close_session(session)