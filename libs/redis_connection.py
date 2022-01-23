import os
from redis import Redis


def get() -> Redis:
    return Redis.from_url(os.environ['REDIS_URL'])
