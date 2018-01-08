# import redis
# pool = redis.ConnectionPool()
# redis_op = redis.Redis(connection_pool=pool)
import json

import datasources
redis_op = datasources.get_redis().redis_op()
redis_op.lpush('hot_news_list', *[{"aa": 1, "bb": None}, {'aa': 2, 'bb': '题目'}])
redis_op.expire('hot_news_list', 1)
r = redis_op.lrange('hot_news_list', 0, 1)
print(r)
r = [u.replace('\'', '"').replace('None', 'null') for u in r]
print(r[2]['bb'])
r = [json.loads(u) for u in r]
print(type(r[0]))
redis_op.delete('fff')