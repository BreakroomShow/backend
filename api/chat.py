from fastapi import APIRouter, Depends, Body
from libs import auth, pusher_client


router = APIRouter()


@router.post('/chat/message')
def create_new_message(
        chat_key: str = Body(..., embed=True),
        message: str = Body(..., embed=True, min_length=1, max_length=200),
        credentials: auth.Credentials = Depends(auth.get_credentials),
        pusher_conn: pusher_client.Pusher = Depends(pusher_client.get_pusher_client),
):
    # todo: verify chat key belongs to active game
    # todo: throttling by credential and text

    pusher_conn.trigger(chat_key, 'new_message', {'message': message, 'from': {'id': credentials.id}})

    return 'ok'
