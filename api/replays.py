from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from libs import redis_connection
from models import replay


router = APIRouter()


@router.get('/replays/last')
def get_last(redis_conn: redis_connection.Redis = Depends(redis_connection.get)):
    last_replay = replay.get_by_game_id(redis_conn, 'aaa4b02e-4f12-4482-97a6-692b606f9422')
    if not last_replay:
        raise HTTPException(status_code=404)
    return last_replay
