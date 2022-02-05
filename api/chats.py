import time
from fastapi import APIRouter, Depends, Body, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from libs import auth, pusher_client, redis_connection
from models import replay, game, chat_message


router = APIRouter()


@router.post('/chats/message')
def create_new_message(
        game_id: str = Body(..., embed=True),
        text: str = Body(..., embed=True, min_length=1, max_length=200),
        credentials: auth.Credentials = Depends(auth.get_credentials),
        pusher_conn: pusher_client.Pusher = Depends(pusher_client.get_pusher_client),
        redis_conn: redis_connection.Redis = Depends(redis_connection.get),
):
    # todo: throttling by credential and text

    current_game = game.get_by_id(redis_conn, game_id)
    if not current_game:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    if not game.is_game_current(redis_conn, game_id):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

    message = chat_message.ChatMessage(text=text, from_id=credentials.id)

    pusher_conn.trigger(current_game.socket_key(), pusher_client.CHAT_MESSAGE_EVENT_NAME, message.dict())
    replay.record_chat_message(redis_conn, game_id, time.time(), message)

    return 'ok'
