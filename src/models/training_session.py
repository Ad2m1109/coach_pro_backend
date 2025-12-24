from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TrainingSessionBase(BaseModel):
    title: str
    date: datetime
    focus: str
    icon_name: str

class TrainingSessionCreate(TrainingSessionBase):
    pass

class TrainingSession(TrainingSessionBase):
    id: str

    class Config:
        from_attributes = True
