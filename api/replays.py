from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from libs import redis_connection
from models import replay


router = APIRouter()


@router.get('/replays/last', response_model=replay.Replay)
def get_last(redis_conn: redis_connection.Redis = Depends(redis_connection.get)):
    last_replay = replay.get_last(redis_conn)
    if not last_replay:
        raise HTTPException(status_code=404)
    return last_replay
