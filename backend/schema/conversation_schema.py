from pydantic import BaseModel
from datetime import datetime


class ConversationResponse(BaseModel):
    success: bool
    conversation_id: int
    conversation_type: str
    filename: str
    transcript: str
    created_at: datetime