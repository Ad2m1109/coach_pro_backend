from pydantic import BaseModel
from typing import Optional
from enum import Enum

class EventTypeEnum(str, Enum):
    goal = "goal"
    assist = "assist"
    yellow_card = "yellow_card"
    red_card = "red_card"
    sub_in = "sub_in"
    sub_out = "sub_out"

class MatchEventBase(BaseModel):
    match_id: Optional[str] = None
    player_id: Optional[str] = None
    event_type: EventTypeEnum
    minute: int
    video_timestamp: Optional[float] = None
    coordinates: Optional[str] = None

class MatchEventCreate(MatchEventBase):
    pass

class MatchEvent(MatchEventBase):
    id: str

    class Config:
        from_attributes = True
