import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, validator
from redis import Redis


_REDIS_KEY_PREFIX = 'game:'
_CURRENT_GAME_ID_REDIS_KEY = 'current_game_id'


class Game(BaseModel):
    id: str
    chain_name: str
    chain_start_time: datetime

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda x: x.timestamp()
        }

    @validator('id', pre=True)
    def set_id(cls, id):
        return id or str(uuid.uuid4())

    @validator('chain_start_time', pre=True)
    def set_chain_start_time(cls, value):
        if type(value) in [int, float]:
            value = datetime.utcfromtimestamp(value)
        return value.replace(tzinfo=timezone.utc)

    def socket_key(self):
        return f'socket_{self.id}'


def create(redis_conn: Redis, game_meta: Game) -> bool:
    key = _REDIS_KEY_PREFIX + game_meta.id
    if redis_conn.get(key):
        return False
    redis_conn.set(key, game_meta.json(), nx=True)
    return True


def get_by_id(redis_conn: Redis, id: str) -> Optional[Game]:
    stored = redis_conn.get(_REDIS_KEY_PREFIX + id)
    if not stored:
        return None
    return Game(**json.loads(stored.decode('utf-8')))


# TODO: Handle concurrency correctly
def mark_current(redis_conn: Redis, id: str):
    redis_conn.set(_CURRENT_GAME_ID_REDIS_KEY, id)


def remove_current_mark(redis_conn: Redis, id: str):
    redis_conn.delete(_CURRENT_GAME_ID_REDIS_KEY)


def is_game_current(redis_conn: Redis, id: str) -> bool:
    saved_game_id = redis_conn.get(_CURRENT_GAME_ID_REDIS_KEY)
    if not saved_game_id:
        return False
    return saved_game_id.decode('utf-8') == id


def get_current(redis_conn: Redis) -> Optional[Game]:
    saved_game_id = redis_conn.get(_CURRENT_GAME_ID_REDIS_KEY)
    if not saved_game_id:
        return None
    return get_by_id(redis_conn, saved_game_id.decode('utf-8'))
