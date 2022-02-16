import os
from pusher import Pusher
from pusher_push_notifications import PushNotifications

CHAT_MESSAGE_EVENT_NAME = 'new_message'


def get_pusher_client() -> Pusher:
    return Pusher(
        app_id=os.environ['PUSHER_APP_ID'],
        key=os.environ['PUSHER_KEY'],
        secret=os.environ['PUSHER_SECRET']
    )


def get_beams_client() -> PushNotifications:
    return PushNotifications(
        instance_id=os.environ['PUSHER_BEAMS_INSTANCE_ID'],
        secret_key=os.environ['PUSHER_BEAMS_SECRET_KEY'],
    )
