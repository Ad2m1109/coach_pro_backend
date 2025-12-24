from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum
from decimal import Decimal # New import

class PositionEnum(str, Enum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"

class FootEnum(str, Enum):
    left = "left"
    right = "right"

class PlayerBase(BaseModel):
    team_id: Optional[str] = None
    name: str
    position: Optional[PositionEnum] = None
    jersey_number: Optional[int] = None
    birth_date: Optional[date] = None
    dominant_foot: Optional[FootEnum] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    nationality: Optional[str] = None
    country_code: Optional[str] = None
    image_url: Optional[str] = None
    market_value: Optional[Decimal] = None # New field

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: str

    class Config:
        from_attributes = True
