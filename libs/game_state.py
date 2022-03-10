from enum import Enum
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
from models import chat_message


class EventType(Enum):
    game_info_splash = 'game_info_splash'
    question_fact = 'question_fact'
    crypto_fact = 'crypto_fact'
    question = 'question'
    answer_reveal = 'answer_reveal'
    planned_chat_message = 'planned_chat_message'
    viewer_count_update = 'viewer_count_update'
    intro_splash = 'intro_splash'


class DistributionType(Enum):
    chain = 'chain'
    socket = 'socket'


class BaseEvent(BaseModel):
    type: EventType
    distribution_type: DistributionType
    duration: Optional[float]  # None if event should only update the state
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


class IntroSplash(BaseEvent):
    type = EventType.intro_splash
    distribution_type = DistributionType.socket
    duration = 10.0


class GameInfoSplash(BaseEvent):
    type = EventType.game_info_splash
    distribution_type = DistributionType.socket
    duration = 10.0
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


class PlannedChatMessage(BaseEvent):
    type = EventType.planned_chat_message
    distribution_type = DistributionType.socket
    duration: Optional[float] = None
    text: str
    from_id: str

    def to_message(self):
        return chat_message.ChatMessage(id=None, text=self.text, from_id=self.from_id)


class ViewerCountUpdate(BaseEvent):
    type = EventType.viewer_count_update
    distribution_type = DistributionType.socket
    duration: Optional[float] = None
    viewer_count: int


AnyEvent = Union[Question, AnswerReveal, GameInfoSplash, IntroSplash, QuestionFact, CryptoFact, PlannedChatMessage, ViewerCountUpdate]


class Scenario(BaseModel):
    events: List[BaseEvent]
