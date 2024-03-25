import redis
from config import config


class RedisService:
    redis_client = None

    @classmethod
    def get_client(cls):
        if not cls.redis_client:
            try:
                cls.redis_client = redis.from_url(config.REDIS_BROKER_URL)
            except Exception as e:
                raise e
        return cls.redis_client
