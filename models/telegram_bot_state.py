from enum import Enum
import redis

_REDIS_HASH_KEY = 'telegram_bot_state'


class TelegramBotState(Enum):
    no_history = 'no_history'
    initial_message_sent = 'initial_message_sent'
    stopped = 'stopped'


def get(redis_conn: redis.Redis, telegram_user_id: int) -> TelegramBotState:
    stored = redis_conn.hget(_REDIS_HASH_KEY, str(telegram_user_id))
    if not stored:
        return TelegramBotState.no_history
    return TelegramBotState[stored.decode('utf-8')]


def update(redis_conn: redis.Redis, telegram_user_id: int, new_state: TelegramBotState):
    redis_conn.hset(_REDIS_HASH_KEY, str(telegram_user_id), new_state.value)
