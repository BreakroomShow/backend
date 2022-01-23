from fastapi import APIRouter, Depends
from libs import redis_connection
from models import game


router = APIRouter()


@router.get('/games/current')
def get_current(redis_conn: redis_connection.Redis = Depends(redis_connection.get)):
    current_game = game.get_current(redis_conn)
    if not current_game:
        return {
            'current_game': None
        }
    return {
        'current_game': {
            'socket_key': current_game.socket_key(),
        }
    }


@router.get('/games/upcoming')
def get_upcoming():
    return []

