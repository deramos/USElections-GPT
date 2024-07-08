import redis
from config import config


class RedisService:
    _redis_client = None

    @classmethod
    def get_client(cls):
        """
        Creates an instance of a redis client if the existing client is None
        :return: redis_client -> Redis
        """
        if not cls._redis_client:
            try:
                cls._redis_client = redis.from_url(config.REDIS_BROKER_URL)
            except Exception as e:
                raise e
        return cls._redis_client
