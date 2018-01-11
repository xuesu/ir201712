import datetime

import datasources
import entities.news
import entities.review
import utils.utils


def split_sql(fin):
    buff = ''
    for line in fin:
        if not line.startswith('--') and line.strip():
            buff += line
            if buff.strip().endswith(';'):
                buff = buff.strip()
                buff = buff[buff.index(' ') + 1:]
                yield buff.strip()
                buff = ''


def import_sql(news_sql_fname, review_sql_fname):
    session = datasources.get_db().create_session()
    prefix = 'INTO `news` (`from`, `news_id`, `url`, `title`, `keywords`, `media_name`, `abstract`, `content`, `time`, `review_num`, `related_id`) VALUES '
    news_id2id = {}
    with open(news_sql_fname) as fin:
        for sql_text in split_sql(fin):
            assert sql_text.startswith(prefix)
            sql_text = sql_text[len(prefix):-1]
            vs = eval(sql_text)
            news_obj = datasources.get_db().find_news_by_url(session, vs[2])
            if news_obj is None:
                news_obj = entities.news.NewsPlain()
                if vs[0] == 'sina':
                    news_obj.source = news_obj.SourceEnum.sina
                elif vs[0] == 'tencent':
                    news_obj.source = news_obj.SourceEnum.tencent
                elif vs[0] == 'toutiao':
                    news_obj.source = news_obj.SourceEnum.toutiao
                else:
                    news_obj.source = news_obj.SourceEnum.ifeng
                news_obj.url = vs[2]
                news_obj.title = vs[3]
                news_obj.keywords = vs[4]
                news_obj.media_name = vs[5]
                news_obj.abstract = vs[6]
                news_obj.content = vs[7]
                news_obj.time = utils.utils.parse_timestr(vs[8])
                news_obj.review_num = vs[9]
                if news_obj.abstract is None or not news_obj.abstract.strip():
                    news_obj.abstract = news_obj.content[:150]
                utils.utils.remove_wild_char_in_news(news_obj)

                news_obj = datasources.get_db().upsert_word_or_word_list(session, news_obj)
            news_id2id[vs[1]] = news_obj.id

    prefix = 'INTO `reviews` (`id`, `news_id`, `user_id`, `user_name`, `area`, `content`, `time`, `agree`) VALUES '
    with open(review_sql_fname) as fin:
        for sql_text in split_sql(fin):
            assert sql_text.startswith(prefix)
            sql_text = sql_text[len(prefix):-1]
            vs = eval(sql_text)
            review_obj = entities.review.ReviewPlain()
            if vs[1] not in news_id2id:
                continue
            review_obj.news_id = news_id2id[vs[1]]
            review_obj.user_id = vs[2]
            review_obj.user_name = vs[3]
            review_obj.content = vs[5]
            review_obj.time = utils.utils.parse_timestr(vs[6])
            review_obj.agree = vs[7]
            utils.utils.remove_wild_char_in_review(review_obj)
            session.merge(review_obj)


if __name__ == '__main__':
    import_sql('/media/xinyi/5D72-B641/Working_on/sql_news/news.sql',
               '/media/xinyi/5D72-B641/Working_on/sql_news/reviews.sql')
