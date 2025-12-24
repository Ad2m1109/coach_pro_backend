from pydantic import BaseModel
from typing import Optional
from enum import Enum

class StaffRoleEnum(str, Enum):
    head_coach = "head_coach"
    assistant_coach = "assistant_coach"
    physio = "physio"
    analyst = "analyst"

class StaffBase(BaseModel):
    team_id: Optional[str] = None
    name: str
    role: Optional[StaffRoleEnum] = None

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    id: str

    class Config:
        from_attributes = True
