from enum import Enum
import hashlib
from typing import Iterable, Optional
import redis


_SET_REDIS_KEY = 'notification_set_'
_HASH_REDIS_KEY = 'notification_hash_'


class SetTarget(Enum):
    telegram = 'telegram'
    email = 'email'


def get_entry_by_user_id(redis_conn: redis.Redis, target: SetTarget, user_id: str) -> Optional[str]:
    stored = redis_conn.hget(_HASH_REDIS_KEY + target.value, user_id)
    if not stored:
        return None
    return stored.decode('utf-8')


def add_entry(redis_conn: redis.Redis, target: SetTarget, entry: str, user_id: Optional[str] = None):
    if user_id:
        redis_conn.hset(_HASH_REDIS_KEY + target.value, user_id, entry)
    else:
        redis_conn.sadd(_SET_REDIS_KEY + target.value, entry)


def delete_entry(redis_conn: redis.Redis, target: SetTarget, entry: str):
    redis_conn.srem(_SET_REDIS_KEY + target.value, entry)


def delete_entry_by_user_id(redis_conn: redis.Redis, target: SetTarget, user_id: str):
    redis_conn.hdel(_HASH_REDIS_KEY + target.value, user_id)


def list_entries(redis_conn: redis.Redis, target: SetTarget, partitions: int = 1, partition_ind: int = 0) -> Iterable[str]:
    for entry_bytes in redis_conn.sscan_iter(_SET_REDIS_KEY + target.value):
        if int(hashlib.sha256(entry_bytes).hexdigest(), 16) % partitions == partition_ind:
            yield entry_bytes.decode('utf-8')
    for _, entry_bytes in redis_conn.hscan_iter(_HASH_REDIS_KEY + target.value):
        if int(hashlib.sha256(entry_bytes).hexdigest(), 16) % partitions == partition_ind:
            yield entry_bytes.decode('utf-8')

