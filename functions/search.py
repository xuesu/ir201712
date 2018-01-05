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
        return [(posting.news_id, [(rd, posting.word_id, posting.news_id,posting.tf,
                                    posting.content_positions, posting.title_positions)]) for posting in rd.posting_list]

    def BM25score(rd, N):
        score = 0
        for news_id, px in rd:
            idf = math.log(N/(px[0].df + 1)) + 1
            score += bm25(idf, px[3])
        return rd[0], score

    index = indexes.vocab_index.VocabIndex()
    posting_lists = index.collect(word_text_list)  # here is multiple posting-list set
    candidate_set = dict()  # store news_id: (news, bm25, time, agree_num)

    posting_lists_4spark = config.get_spark_context().parallelized(posting_lists)
    news2words = posting_lists_4spark.flatMap(news_id2words).groupByKey()

    if ranking == RELEVENCE_RANKING:
        N = len(news2words)
        ranking_set = news2words.Map(lambda rd, N: BM25score(rd, N=N))
        return [(news_id, score) for news_id, score in ranking_set].sort(key=lambda k: k[1], reverse=True)
    if ranking == TIME_DESCEND_RANKING:
        pass
    if ranking == TIME_INCREASE_RANKING:
        pass
    if ranking == HOT_RANKING:
        pass
    # need to ranking
    return [(rd[0], 1) for rd in news2words]


def universal_search(session, search_text, ranking, page, num_in_page=10):
    # segment search_text. TODO
    word_regex_list = search_text.split(' ')
    fl = '*' in ''.join(word_regex_list)
    if fl:
        word_text_list = functions.suggest.suggest_similar_search(word_regex_list, 1)[0]
    else:
        word_text_list = word_regex_list
    ranking_set = search(word_text_list, ranking)
    # need to return Length of ranking_set,[news_brief]

    candidate_id_list = [u[0] for u in ranking_set[(page-1)*num_in_page: page*num_in_page]]
    result_list = [{'news_id': row.source_id,
                    'title': row.title,
                    'source': row.source,
                    'time': row.time,
                    'id': row.id} for row in datasources.get_db().find_news_brief_by_id(session, candidate_id_list)]
    for r in result_list:
        for k, v in ranking_set[(page-1)*num_in_page: page*num_in_page]:
            if k == r['id']:
                r['score'] = v
                break
    return len(ranking_set), result_list, ' '.join(word_text_list)
