from libs import pusher_client, telegram_bot, redis_connection, mailgun
from models import notification_set

PUSHER_WEB_PUSH_PUSHER_INTEREST = 'game-reminders'

_WEB_PUSH_TITLE = 'Breakroom'
_WEB_PUSH_TEXT = 'The Breakroom game starts in 5 minutes! Join now to win crypto.'

_TELEGRAM_TEXT = 'The Breakroom game starts in 5 minutes! Join now to win crypto: https://breakroom.show/'

_EMAIL_SUBJECT = 'Breakroom starts'
_EMAIL_TEXT = 'The Breakroom game starts in 5 minutes. You can join the game by this link: https://breakroom.show/'


def _send_web_push(beams_client: pusher_client.PushNotifications):
    beams_client.publish_to_interests(
        interests=[PUSHER_WEB_PUSH_PUSHER_INTEREST],
        publish_body={
            'web': {
                'time_to_live': 360,
                'notification': {
                    'title': _WEB_PUSH_TITLE,
                    'body': _WEB_PUSH_TEXT,
                    'deep_link': "https://breakroom.show",
                    'hide_notification_if_site_has_focus': True,
                },
            },
        }
    )


def _send_emails(redis_conn: redis_connection.Redis):
    for email in notification_set.list_entries(redis_conn, notification_set.SetTarget.email):
        mailgun.send_message(email, _EMAIL_SUBJECT, _EMAIL_TEXT)


def _send_telegram(redis_conn: redis_connection.Redis, bot: telegram_bot.Bot):
    for telegram_user_id in notification_set.list_entries(redis_conn, notification_set.SetTarget.telegram):
        bot.send_message(telegram_user_id, _TELEGRAM_TEXT)


def send():
    redis_conn = redis_connection.get()

    beams_client = pusher_client.get_beams_client()
    _send_web_push(beams_client)

    telegram_bot_instance = telegram_bot.get_instance()
    _send_telegram(redis_conn, telegram_bot_instance)

    _send_emails(redis_conn)

