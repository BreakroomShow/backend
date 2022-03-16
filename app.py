import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import account, chats, games, notifications, replays, telegram_bot
from libs import telegram_bot as telegram_bot_lib

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(account.router)
app.include_router(chats.router)
app.include_router(games.router)
app.include_router(notifications.router)
app.include_router(replays.router)
app.include_router(telegram_bot.router)

telegram_bot_lib.register(telegram_bot_lib.get_instance(), f'/telegramBot/update?secret={os.environ["TELEGRAM_BOT_URL_SECRET"]}')
