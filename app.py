from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import account, chat, games

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
app.include_router(chat.router)
app.include_router(games.router)
