# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import datetime
import pandas
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm

import config
import entities
import entities.news  # essential to create all tables
import entities.review
import entities.words
import logs.loggers

logger = logs.loggers.LoggersHolder().get_logger("datasource")


class MySQLDataSource(object):
    def __init__(self, testing=False):
        datasource_config = config.datasource_config
        self.testing = testing
        self.database_name = datasource_config.test_database_name if testing else datasource_config.database_name
        self.session_pool = list()
        self.former_action = dict()
        self.engine = self.connect()
        self.session_maker = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)
        self.scope_session_maker = sqlalchemy.orm.scoped_session(self.session_maker)
        if (testing or datasource_config.rebuild) and config.spark_config.driver_mode:
            self.drop_all_tables()
        self.create_all_tables()

    def __del__(self):
        self.close_all_session()

    def create_session(self):
        session = self.scope_session_maker()
        self.session_pool.append(session)
        return session

    def close_session(self, session):
        try:
            self.commit_session(session)
        except sqlalchemy.exc.InvalidRequestError as e:
            logger.error(e)
            self.session_pool.remove(session)
        session.close()

    def close_all_session(self):
        session_pool = [session for session in self.session_pool]
        for session in session_pool:
            self.close_session(session)
        self.session_pool = list()

    def commit_session(self, session):
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(e)

    def connect(self):
        datasource_config = config.datasource_config
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(
                datasource_config.user, datasource_config.password,
                datasource_config.host, datasource_config.port,
                self.database_name
            ),
            encoding="utf-8",
            pool_size=datasource_config.pool_size,
            max_overflow=datasource_config.max_overflow,
            pool_timeout=datasource_config.timeout
        )
        return engine

    def create_all_tables(self):
        entities.SQLALCHEMY_BASE.metadata.create_all(self.engine)

    def drop_all_tables(self, forced=True):
        """
        will DROP all tables!
        :return:
        """
        if forced:
            self.close_all_session()
        entities.SQLALCHEMY_BASE.metadata.drop_all(self.engine)

    def recreate_all_tables(self):
        self.drop_all_tables()
        self.create_all_tables()

    def upsert_one_or_many(self, session, obj, commit_now=True):
        if isinstance(obj, list):
            ans = list()
            for o in obj:
                ans.append(session.merge(o))
        else:
            ans = session.merge(obj)
        if commit_now:
            self.commit_session(session)
        return ans

    def find(self, session, qentities,
             filter_by_condition=None, order_by_condition=None, filter_condition=None, limit=None,
             options=None, pandas_format=False, first=False):
        if isinstance(qentities, list):
            query = session.query(*qentities)
        else:
            query = session.query(qentities)
        if filter_by_condition is not None:
            query = query.filter_by(**filter_by_condition)
        if filter_condition is not None:
            query = query.filter(filter_condition)
        if order_by_condition is not None:
            query = query.order_by(order_by_condition)
        if limit is not None:
            query = query.limit(limit)
        if options is not None:
            if isinstance(options, list):
                for option in options:
                    query = query.options(option)
            else:
                query = query.options(options)
        if pandas_format:
            return pandas.read_sql_query(query.statement, self.engine)
        elif first:
            return query.first()
        else:
            return query.all()

    def delete(self, session, obj, commit_now=True):
        session.delete(obj)
        if commit_now:
            self.commit_session(session)

    def upsert_news_or_news_list(self, session, news, commit_now=True):
        return self.upsert_one_or_many(session, news, commit_now)

    def find_news_list(self, session):
        return self.find(session, entities.news.NewsPlain)

    def find_news_by_id(self, session, id):
        ans_list = self.find(session, entities.news.NewsPlain, filter_by_condition={"id": id})
        if ans_list:
            return ans_list[0]
        return None

    def find_news_by_source_id(self, session, source_id):
        ans_list = self.find(session, entities.news.NewsPlain, filter_by_condition={"source_id": source_id})
        if ans_list:
            return ans_list[0]
        return None

    def find_news_plain_text(self, session):
        return self.find(session, [entities.news.NewsPlain.id, entities.news.NewsPlain.title,
                                   entities.news.NewsPlain.content], pandas_format=True)

    def find_news_abstract_by_source_id(self, session, source_id):
        return self.find(session, entities.news.NewsPlain.abstract, filter_by_condition={'source_id': source_id}, first=True)

    def find_news_brief_by_id(self, session, id_list):
        return self.find(session, [entities.news.NewsPlain.source, entities.news.NewsPlain.source_id,
                                   entities.news.NewsPlain.title, entities.news.NewsPlain.time,
                                   entities.news.NewsPlain.id],
                         filter_condition=entities.news.NewsPlain.id.in_(id_list))

    def find_news_time_and_review_num_by_id(self, session, id_list):
        return self.find(session, [entities.news.NewsPlain.id, entities.news.NewsPlain.time, entities.news.NewsPlain.review_num],
                         filter_condition=entities.news.NewsPlain.id.in_(id_list),
                         order_by_condition=sqlalchemy.desc(entities.news.NewsPlain.time))

    def find_news_title_by_source_id_list(self, session, source_id_list):  # TODO: need to test
        return self.find(session, [entities.news.NewsPlain.source_id,
                         entities.news.NewsPlain.title],
                         filter_condition=entities.news.NewsPlain.source_id.in_(source_id_list))

    def find_hot_news(self, session, num, review_num=50, delta_day=100):  # FIXME: review_num >=50, delta time < 1d
        current_time = datetime.datetime.utcnow()
        one_day_ago = current_time - datetime.timedelta(days=delta_day)
        return self.find(session, [entities.news.NewsPlain.source_id,
                                   entities.news.NewsPlain.title,
                                   entities.news.NewsPlain.abstract,
                                   entities.news.NewsPlain.time,
                                   entities.news.NewsPlain.media_name,
                                   entities.news.NewsPlain.keywords],
                         filter_condition=(entities.news.NewsPlain.time > one_day_ago),
                         order_by_condition=sqlalchemy.desc(entities.news.NewsPlain.review_num),
                         limit=num
                         )

    def find_reviews_by_news_id(self, session, news_id):
        return self.find(session, entities.review.ReviewPlain, filter_by_condition={'news_id': news_id})

    def upsert_word_or_word_list(self, session, word, commit_now=True):
        return self.upsert_one_or_many(session, word, commit_now)

    def find_word_list(self, session):
        return self.find(session, entities.words.Word, options=(sqlalchemy.orm.undefer("df"),
                                                                sqlalchemy.orm.undefer("cf")))

    def find_word_by_text(self, session, text):
        ans_list = self.find(session, entities.words.Word, filter_by_condition={"text": text})
        if ans_list:
            return ans_list[0]
        return None

    def delete_word(self, session, word, commit_now=True):
        self.delete(session, word, commit_now)

    def find_word_posting_list_by_word_id(self, session, word_id, news_id=None):
        filter_by_condition = {"word_id": word_id}
        if news_id is not None:
            filter_by_condition = {"word_id": word_id, "news_id": news_id}
        return self.find(session, entities.words.WordPosting, filter_by_condition=filter_by_condition)

    def find_word_plain_text_ordered_by_text(self, session):
        ans = self.find(session, [entities.words.Word.text], order_by_condition="text")
        return [a[0] for a in ans]
