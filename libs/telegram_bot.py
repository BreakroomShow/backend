import os
import redis
import telegram
from telegram import Bot
from models import telegram_bot_state, notification_set

_RESPONSE_INITIAL = ('Hey! Thank you for setting up your notifications. The bot will send you a message 10 minutes before '
                     'every Breakroom game. \n\nIf you want to stop receiving these messages, send /stop.\n\n'
                     'You can also follow us on Twitter for game announcements: https://twitter.com/playbreakroom')
_RESPONSE_DEFAULT = ('The bot will send you a message 10 minutes before every Breakroom game. If you want to stop '
                     'receiving these messages, send /stop.\n\nYou can also follow us on Twitter for game announcements: https://twitter.com/playbreakroom.'
                     ' We can answer your questions there too!')
_RESPONSE_STOPPED = 'We stopped sending you notifications about the Breakroom games. If you want to resubscribe, send /restart.'
_RESPONSE_REENABLED_ = 'Awesome! We re-enabled notifications for you. If you want to pause again, send us /stop.'


# FastAPI dependency
def get_instance():
    return Bot(os.environ['TELEGRAM_BOT_TOKEN'])


def register(bot: Bot, path):
    bot.set_webhook(url=os.environ['RENDER_EXTERNAL_URL'] + path)


def handle_update(bot: Bot, redis_conn: redis.Redis, update: telegram.update.Update):
    if not update.message:
        return
    user_id = update.message.from_user.id
    text = update.message.text
    current_state = telegram_bot_state.get(redis_conn, user_id)

    if current_state == telegram_bot_state.TelegramBotState.no_history:
        notification_set.add_entry(redis_conn, notification_set.SetTarget.telegram, str(user_id))
        bot.send_message(user_id, text=_RESPONSE_INITIAL)
        telegram_bot_state.update(redis_conn, user_id, telegram_bot_state.TelegramBotState.initial_message_sent)
    elif current_state == telegram_bot_state.TelegramBotState.initial_message_sent and text == '/stop':
        notification_set.delete_entry(redis_conn, notification_set.SetTarget.telegram, str(user_id))
        bot.send_message(user_id, text=_RESPONSE_STOPPED)
        telegram_bot_state.update(redis_conn, user_id, telegram_bot_state.TelegramBotState.stopped)
    elif current_state == telegram_bot_state.TelegramBotState.initial_message_sent:
        bot.send_message(user_id, text=_RESPONSE_DEFAULT)
        # Keep same state
    elif current_state == telegram_bot_state.TelegramBotState.stopped and text == '/restart':
        notification_set.add_entry(redis_conn, notification_set.SetTarget.telegram, str(user_id))
        bot.send_message(user_id, text=_RESPONSE_REENABLED_)
        telegram_bot_state.update(redis_conn, user_id, telegram_bot_state.TelegramBotState.initial_message_sent)
    elif current_state == telegram_bot_state.TelegramBotState.stopped:
        bot.send_message(user_id, text=_RESPONSE_STOPPED)
        # Keep same state




