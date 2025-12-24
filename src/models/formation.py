from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class FormationBase(BaseModel):
    name: str
    description: Optional[str] = None
    positions: Optional[List[Any]] = None
    user_id: Optional[str] = None

class FormationCreate(FormationBase):
    pass

class Formation(FormationBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
