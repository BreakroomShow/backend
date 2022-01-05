from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class EventType(Enum):
    game_info_splash = 'game_info_splash'
    question_fact = 'question_fact'
    crypto_fact = 'crypto_fact'
    question = 'question'
    answer_reveal = 'answer_reveal'


class DistributionType(Enum):
    chain = 'chain'
    socket = 'socket'


# question and answer


class BaseEvent(BaseModel):
    type: EventType
    distribution_type: DistributionType
    duration: float
    game_start_offset: float


class Question(BaseModel):
    type = EventType.question


class GameInfoSplash(BaseEvent):
    type = EventType.game_info_splash
    distribution_type = DistributionType.socket
    players: int
    prize_fund_usd: int
    sponsor_title: str


class QuestionFact(BaseEvent):
    type = EventType.question_fact
    distribution_type = DistributionType.socket
    text: str
    image_url: Optional[str]


class CryptoFact(BaseEvent):
    type = EventType.crypto_fact
    distribution_type = DistributionType.socket
    text: str
    image_url: Optional[str]


class Scenario(BaseModel):
    events = List[BaseEvent]
