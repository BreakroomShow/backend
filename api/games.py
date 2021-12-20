from fastapi import APIRouter


router = APIRouter()


@router.get('/games/current')
def get_current():
    return {
        'chat_key': 'test-chat-room'
    }


@router.get('/games/upcoming')
def get_upcoming():
    return []

