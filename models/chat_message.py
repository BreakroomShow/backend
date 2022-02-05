from pydantic import BaseModel


class ChatMessage(BaseModel):
    text: str
    from_id: str
