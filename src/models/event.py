from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    name: str

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True