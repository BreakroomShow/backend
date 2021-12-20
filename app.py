from fastapi import FastAPI

from api import account, chat, games

app = FastAPI()

app.include_router(account.router)
app.include_router(chat.router)
app.include_router(games.router)
