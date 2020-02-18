import logging

from django_redis.client import default

logger = logging.getLogger(__name__)


class RedisClient(default.DefaultClient):
    def get(self, key, default=None, version=None, client=None):
        try:
            return super().get(key, default=default, version=version, client=client)
        except ValueError as e:
            if "unsupported pickle protocol" in str(e):
                # pickle deserialization error
                logger.warn("Error while deserializing pickle value from cache")
                return default
            else:
                raise

    def get_many(self, *args, **kwargs):
        try:
            return super().get_many(*args, **kwargs)
        except ValueError as e:
            if "unsupported pickle protocol" in str(e):
                # pickle deserialization error
                logger.warn("Error while deserializing pickle value from cache")
                return {}
            else:
                raise
