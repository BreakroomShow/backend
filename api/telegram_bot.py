import os
from fastapi import APIRouter, Depends, Request, HTTPException
from telegram import Bot, Update
from libs import redis_connection, telegram_bot

router = APIRouter()


@router.post('/telegramBot/update')
async def telegram_update_webhook(
        request: Request,
        secret: str,
        redis_conn: redis_connection.Redis = Depends(redis_connection.get),
        telegram_bot_instance: Bot = Depends(telegram_bot.get_instance),
):
    if secret != os.environ['TELEGRAM_BOT_URL_SECRET']:
        raise HTTPException(status_code=400)
    request_data = await request.json()
    update = Update.de_json(request_data, bot=telegram_bot_instance)
    telegram_bot.handle_update(telegram_bot_instance, redis_conn, update)
    return 'ok'
