# -*- coding:utf-8 -*-
"""
@author: xuesu

"""
import pandas
import sqlalchemy
import sqlalchemy.orm

import config.config_manager
import entities
import entities.news  # essential to create all tables
import entities.review
import entities.words

datasource_config = config.config_manager.ConfigManager().datasource_config


class MySQLDataSource(object):
    def __init__(self, testing=False):
        self.testing = testing
        self.database_name = datasource_config.test_database_name if testing else datasource_config.database_name
        self.engine = self.connect()
        if datasource_config.rebuild and config.config_manager.ConfigManager().driver_mode:
            self.drop_all_tables()
        self.create_all_tables()
        self.session_maker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.scope_session_maker = sqlalchemy.orm.scoped_session(self.session_maker)

    def create_session(self):
        return self.scope_session_maker()

    def close_session(self, session):
        session.close()

    def connect(self):
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(
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

    def upsert_news(self, session, news):
        news = session.merge(news)
        session.commit()
        return news

    def create_all_tables(self):
        entities.SQLALCHEMY_BASE.metadata.create_all(self.engine)

    def drop_all_tables(self):
        """
        will DROP all tables!
        :return:
        """
        entities.SQLALCHEMY_BASE.metadata.drop_all(self.engine)

    def find_news_list(self, session, filter_by_condition=None, order_by_condition=None):
        query = session.query(entities.news.NewsPlain).options(sqlalchemy.orm.lazyload('reviews'))
        if filter_by_condition is not None:
            query = query.filter_by(**filter_by_condition)
        if order_by_condition is not None:
            query = query.order_by(order_by_condition)
        return query.all()

    def find_news_by_source_id(self, session, source_id):
        news_list = self.find_news_list(session, {"source_id": source_id})
        if len(news_list) == 0:
            return None
        else:
            return news_list[0]

    def find_news_plain_text(self, session, filter_by_condition=None):
        query = session.query(entities.news.NewsPlain.id, entities.news.NewsPlain.title,
                              entities.news.NewsPlain.content)
        if filter_by_condition is not None:
            query = query.filter_by(**filter_by_condition)
        return pandas.read_sql_query(query.statement, self.engine)

    def upsert_word(self, session, word):
        word = session.merge(word)
        session.commit()
        return word

    def find_word_list(self, session, filter_by_condition=None, order_by_condition=None):
        query = session.query(entities.words.Word).options(sqlalchemy.orm.lazyload('posting_list'))
        if filter_by_condition is not None:
            query = query.filter_by(**filter_by_condition)
        if order_by_condition is not None:
            query = query.order_by(order_by_condition)
        return query.all()

    def find_word_by_text(self, session, text):
        word_list = self.find_word_list(session, {"text": text})
        if len(word_list) == 0:
            return None
        else:
            return word_list[0]

    def find_word_posting_list(self, session, filter_by_condition):
        query = session.query(entities.words.WordPosting)
        if filter_by_condition is not None:
            query = query.filter_by(**filter_by_condition)
        return query.all()

    def find_word_posting_list_by_word_id(self, session, word_id):
        return self.find_word_posting_list(session, {"word_id": word_id})
