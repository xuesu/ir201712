import redis

import config
import logs.loggers

logger = logs.loggers.LoggersHolder().get_logger("redis_datasource")


class RedisDataSource(object):
    def __init__(self):
        self.pool = None

    @staticmethod
    def __pool__():
        redis_config = config.cache_config
        return redis.ConnectionPool(host=redis_config.redis_host, port=redis_config.redis_port,
                                    decode_responses=True)

    def redis_op(self):
        if self.pool is None:
            self.pool = self.__pool__()
        return redis.Redis(connection_pool=self.pool)
