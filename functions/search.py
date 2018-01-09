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
def search(word_text_list, ranking):
    def news_id2words(rd):
        return [(posting.news_id, (rd.df, posting.word_id, posting.news_id, posting.tf,
                                   posting.content_positions, posting.title_positions)) for posting in rd.posting_list]

    def BM25score(rd):
        N = N_all_documents.value
        score = 0
        for px in rd[1]:
            idf = math.log(N/(px[0] + 1)) + 1
            score += bm25(idf, px[3])
        return rd[0], score

    index = indexes.vocab_index.VocabIndex()
    posting_lists = index.collect(word_text_list)  # here is multiple posting-list set
    posting_lists = list(set(posting_lists))
    print('已有的词汇索引（去除None前）:', posting_lists)
    try:
        posting_lists.remove(None)
    except ValueError:
        pass
    print('已有的词汇索引：', posting_lists)

    # loading all of them if posting_lists is not None.

    for w in posting_lists:
        posting_list = w.posting_list

    posting_lists_4spark = config.get_spark_context().parallelize(posting_lists)
    news2words_set = posting_lists_4spark.flatMap(news_id2words).groupByKey()

    if ranking == RELEVENCE_RANKING:
        N = news2words_set.count()
        N_all_documents = config.get_spark_context().broadcast(N)
        ranking_set = news2words_set.map(BM25score)
        ranking_set_tmp = ranking_set.collect()
        ranking_set_tmp.sort(key=lambda k: k[1], reverse=True)
        return ranking_set_tmp

    if ranking == TIME_DESCEND_RANKING:
        pass
    if ranking == TIME_INCREASE_RANKING:
        pass
    if ranking == HOT_RANKING:
        pass
    # need to ranking
    ranking_set = news2words_set.map(lambda rd: rd[0]).collect()
    return ranking_set

@utils.decorator.timer
def universal_search(session, search_text, ranking, page, num_in_page=10):
    # segment search_text. TODO
    word_regex_list = search_text.split(' ')
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
    regex_search_list = list()
    if fl:
        regex_search_list = functions.suggest.suggest_similar_search(word_regex_list, 1)[0]
    segment_word_4_search_list += regex_search_list
    segment_word_4_search_list = list(set(segment_word_4_search_list))
    print('segment for search: ', segment_word_4_search_list)
    ranking_set = search(segment_word_4_search_list, ranking)
    if ranking != RELEVENCE_RANKING:
        ranking_set = datasources.get_db().find_news_time_and_review_num_by_id(session, ranking_set)
        if ranking == HOT_RANKING:
            ranking_set = [(u.id, u.review_num) for u in ranking_set]
        else:
            ranking_set = [(u.id, u.time) for u in ranking_set]
        if ranking == TIME_INCREASE_RANKING:
            ranking_set.sort(key=lambda k: k[1])
        else:
            ranking_set.sort(key=lambda k: k[1], reverse=True)
    # need to return Length of ranking_set,[news_brief]
    # import pdb
    # pdb.set_trace()
    candidate_id_list = [u[0] for u in ranking_set[(page-1)*num_in_page: page*num_in_page]]
    if len(candidate_id_list) == 0:
        return 0, [], [' '.join(segment_word_4_search_list), regex_search_list]
    result_list = [{'news_id': row.source_id,
                    'title': row.title,
                    # 'source': row.source.sina,
                    'time': row.time,
                    'id': row.id} for row in datasources.get_db().find_news_brief_by_id(session, candidate_id_list)]
    for r in result_list:
        for k, v in ranking_set[(page-1)*num_in_page: page*num_in_page]:
            if r.__contains__('score') is False and k == r['id']:
                r['score'] = v
                break
    result_list.sort(key=lambda r: r['score'], reverse=True if ranking != TIME_INCREASE_RANKING else False)
    return len(ranking_set), result_list, [' '.join(segment_word_4_search_list), regex_search_list]

if __name__ == "__main__":
    config.spark_config.driver_mode = False
    config.spark_config.testing = True
    session = datasources.get_db().create_session()
    L, result_list, good_text = universal_search(session, "科学", 4, 1)
    print(L, result_list, good_text)
    datasources.get_db().close_session(session)