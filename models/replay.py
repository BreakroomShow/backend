import json
from typing import List, Optional
from pydantic import BaseModel
from redis import Redis

from libs import game_state

_STARTED_AT_REDIS_KEY = 'replay_started_at:'
_FINISHED_AT_REDIS_KEY = 'replay_finished_at:'
_EVENTS_LIST_REDIS_KEY = 'replay_events:'
_LAST_REPLAY_REDIS_KEY = 'last_replay_game_id'


class ReplayEvent(BaseModel):
    event: game_state.AnyEvent
    timestamp: float


class Replay(BaseModel):
    game_id: str
    game_started_at_timestamp: float
    game_finished_at_timestamp: float
    events: List[ReplayEvent]


def record_start(redis_conn: Redis, game_id: str, timestamp: float):
    redis_conn.setnx(_STARTED_AT_REDIS_KEY + game_id, timestamp)


def record_finish(redis_conn: Redis, game_id: str, timestamp: float):
    redis_conn.setnx(_FINISHED_AT_REDIS_KEY + game_id, timestamp)


def record_event(redis_conn: Redis, game_id: str, timestamp: float, event: game_state.AnyEvent):
    redis_conn.rpush(_EVENTS_LIST_REDIS_KEY + game_id, ReplayEvent(event=event, timestamp=timestamp).json())


def get_by_game_id(redis_conn: Redis, game_id: str) -> Optional[Replay]:
    started_at_timestamp = redis_conn.get(_STARTED_AT_REDIS_KEY + game_id)
    finished_at_timestamp = redis_conn.get(_FINISHED_AT_REDIS_KEY + game_id)
    if not started_at_timestamp or not finished_at_timestamp:
        return None
    started_at_timestamp = float(started_at_timestamp)
    finished_at_timestamp = float(finished_at_timestamp)

    replay_events = [
        ReplayEvent(**json.loads(replay_event.decode('utf-8')))
        for replay_event in redis_conn.lrange(_EVENTS_LIST_REDIS_KEY + game_id, 0, -1)
    ]

    return Replay(
        game_id=game_id,
        game_started_at_timestamp=started_at_timestamp,
        game_finished_at_timestamp=finished_at_timestamp,
        events=replay_events,
    )


def set_last(redis_conn: Redis, game_id: str):
    redis_conn.set(_LAST_REPLAY_REDIS_KEY, game_id)


def get_last(redis_conn: Redis) -> Optional[Replay]:
    game_id = redis_conn.get(_LAST_REPLAY_REDIS_KEY)
    print(game_id)
    if not game_id:
        return None
    game_id = game_id.decode('utf-8')
    return get_by_game_id(redis_conn, game_id)
