from enum import Enum
from typing import List, Optional, Union, Dict
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


class BaseEvent(BaseModel):
    type: EventType
    distribution_type: DistributionType
    duration: float
    game_start_offset: float

    class Config:
        use_enum_values = True


class Question(BaseEvent):
    type = EventType.question
    distribution_type = DistributionType.chain
    duration = 10.0
    question: str
    answers: List[str]


class AnswerReveal(BaseEvent):
    type = EventType.answer_reveal
    distribution_type = DistributionType.chain
    duration = 5.0
    question: Question
    correct_answer_ind: int
    answer_count: Dict[int, int]  # ind => count


class GameInfoSplash(BaseEvent):
    type = EventType.game_info_splash
    distribution_type = DistributionType.socket
    duration = 5.0
    players: int
    prize_fund_usd: int
    sponsor_title: str


class QuestionFact(BaseEvent):
    type = EventType.question_fact
    distribution_type = DistributionType.socket
    duration = 5.0
    text: str
    image_url: Optional[str]


class CryptoFact(BaseEvent):
    type = EventType.crypto_fact
    distribution_type = DistributionType.socket
    text: str
    image_url: Optional[str]


AnyEvent = Union[Question, AnswerReveal, GameInfoSplash, QuestionFact, CryptoFact]


class Scenario(BaseModel):
    events: List[AnyEvent]
