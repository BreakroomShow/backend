import os
from pusher import Pusher

CHAT_MESSAGE_EVENT_NAME = 'new_message'


def get_pusher_client() -> Pusher:
    return Pusher(
        app_id=os.environ['PUSHER_APP_ID'],
        key=os.environ['PUSHER_KEY'],
        secret=os.environ['PUSHER_SECRET']
    )
