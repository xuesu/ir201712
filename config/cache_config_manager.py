class CacheConfig(object):
    def __init__(self, config_data):
        self.redis_host = config_data["redis_host"]
        self.redis_port = int(config_data["redis_port"])
        self.expire = int(config_data["expire_delta"])