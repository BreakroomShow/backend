import time
from redis import Redis

_REDIS_HASH_KEY = 'used_nonce'


def exists(redis_conn: Redis, nonce: str) -> bool:
    return bool(redis_conn.hget(_REDIS_HASH_KEY, nonce))


def save(redis_conn: Redis, nonce: str):
    redis_conn.hset(_REDIS_HASH_KEY, nonce, int(time.time()))
