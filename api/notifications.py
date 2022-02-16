from typing import Optional
from fastapi import APIRouter, Depends, Body
from pydantic import EmailStr
from libs import auth, redis_connection
from models import notification_set

router = APIRouter()


@router.post('/notifications/email')
async def add_notification_email(
        email: EmailStr = Body(..., embed=True),
        credentials: auth.Credentials = Depends(auth.get_credentials),
        redis_conn: redis_connection.Redis = Depends(redis_connection.get),
):
    return notification_set.add_entry(redis_conn, notification_set.SetTarget.email, email, credentials.id)


@router.get('/notifications/email', response_model=Optional[str])
async def get_notification_email(
        credentials: auth.Credentials = Depends(auth.get_credentials),
        redis_conn: redis_connection.Redis = Depends(redis_connection.get),
):
    return notification_set.get_entry_by_user_id(redis_conn, notification_set.SetTarget.email, credentials.id)
