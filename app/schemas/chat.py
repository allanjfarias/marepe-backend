from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: str
    association_id: str
    sender_id: str
    message_type: str
    content: str
    created_at: datetime


class MessagesHistoryResponse(BaseModel):
    messages: List[MessageResponse]


class CloseAssociationRequest(BaseModel):
    charge_amount: Optional[float] = Field(None, ge=0)
    charge_photo_url: Optional[str] = None
    no_charge: bool = False
