import uuid
from pydantic import BaseModel, validator


class ChatMessage(BaseModel):
    id: str
    text: str
    from_id: str

    @validator('id', pre=True)
    def set_id(cls, id):
        return id or str(uuid.uuid4())
