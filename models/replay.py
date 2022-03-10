import json
from typing import List, Optional, Union
from pydantic import BaseModel
from redis import Redis

from models import chat_message
from libs import game_state

_STARTED_AT_REDIS_KEY = 'replay_started_at:'
_FINISHED_AT_REDIS_KEY = 'replay_finished_at:'
_EVENTS_LIST_REDIS_KEY = 'replay_events:'
_CHAT_MESSAGES_LIST_REDIS_KEY = 'chat_messages:'
_LAST_REPLAY_REDIS_KEY = 'last_replay_game_id'


class ReplayChatMessage(BaseModel):
    message: chat_message.ChatMessage
    timestamp: float


class ReplayEvent(BaseModel):
    event: game_state.BaseEvent
    timestamp: float


class Replay(BaseModel):
    game_id: str
    game_started_at_timestamp: float
    game_finished_at_timestamp: float
    events: List[ReplayEvent]
    chat_messages: List[ReplayChatMessage]


def record_start(redis_conn: Redis, game_id: str, timestamp: float):
    redis_conn.setnx(_STARTED_AT_REDIS_KEY + game_id, timestamp)


def record_finish(redis_conn: Redis, game_id: str, timestamp: float):
    redis_conn.setnx(_FINISHED_AT_REDIS_KEY + game_id, timestamp)


def record_event(redis_conn: Redis, game_id: str, timestamp: float, event: game_state.AnyEvent):
    if event.type == game_state.EventType.planned_chat_message:
        return record_chat_message(redis_conn, game_id, timestamp, event.to_message())
    redis_conn.rpush(_EVENTS_LIST_REDIS_KEY + game_id, ReplayEvent(event=event, timestamp=timestamp).json())


def record_chat_message(redis_conn: Redis, game_id: str, timestamp: float, message: chat_message.ChatMessage):
    redis_conn.rpush(
        _CHAT_MESSAGES_LIST_REDIS_KEY + game_id,
        ReplayChatMessage(message=message, timestamp=timestamp).json(),
    )


def get_by_game_id(redis_conn: Redis, game_id: str) -> Optional[Replay]:
    started_at_timestamp = redis_conn.get(_STARTED_AT_REDIS_KEY + game_id)
    finished_at_timestamp = redis_conn.get(_FINISHED_AT_REDIS_KEY + game_id)
    if not started_at_timestamp or not finished_at_timestamp:
        return None
    started_at_timestamp = float(started_at_timestamp)
    finished_at_timestamp = float(finished_at_timestamp)

    replay_events = [
        ReplayEvent(
            event=game_state.EVENT_TYPE_TO_CLASS[game_state.EventType(replay_event['event']['type'])](**replay_event['event']),
            timestamp=replay_event['timestamp']
        )
        for replay_event in map(json.loads, redis_conn.lrange(_EVENTS_LIST_REDIS_KEY + game_id, 0, -1))
    ]
    chat_messages = [
        ReplayChatMessage(**json.loads(chat_message.decode('utf-8')))
        for chat_message in redis_conn.lrange(_CHAT_MESSAGES_LIST_REDIS_KEY + game_id, 0, -1)
    ]

    return Replay(
        game_id=game_id,
        game_started_at_timestamp=started_at_timestamp,
        game_finished_at_timestamp=finished_at_timestamp,
        events=replay_events,
        chat_messages=chat_messages,
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
