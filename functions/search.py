import utils.utils
import indexes
import functions.suggest
import config
import math
import datasources

RELEVENCE_RANKING = 1
TIME_DESCEND_RANKING = 2
TIME_INCREASE_RANKING = 3
HOT_RANKING = 4


def bm25(idf, tf, fl=1, avgfl=1, B=0.75, K1=1.2):

    return idf * ((tf * (K1 + 1)) / (tf + K1 * ((1 - B) + B * fl / avgfl)))


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
    # loading all of them.
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


def universal_search(session, search_text, ranking, page, num_in_page=10):
    # segment search_text. TODO
    word_regex_list = search_text.split(' ')
    fl = '*' in ''.join(word_regex_list)
    if fl:
        word_text_list = functions.suggest.suggest_similar_search(word_regex_list, 1)[0]
    else:
        word_text_list = word_regex_list
    ranking_set = search(word_text_list, ranking)
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
        return 0, [], ' '.join(word_text_list)
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
    return len(ranking_set), result_list, ' '.join(word_text_list)

if __name__ == "__main__":
    config.spark_config.driver_mode = False
    config.spark_config.testing = True
    session = datasources.get_db().create_session()
    L, result_list, good_text = universal_search(session, "科学", 4, 1)
    print(L, result_list, good_text)
    datasources.get_db().close_session(session)