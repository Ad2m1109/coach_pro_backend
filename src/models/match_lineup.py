from pydantic import BaseModel
from typing import Optional

class MatchLineupBase(BaseModel):
    match_id: str
    team_id: str
    formation_id: Optional[str] = None
    is_starting: bool
    player_id: str
    position_in_formation: Optional[str] = None

class MatchLineupCreate(MatchLineupBase):
    pass

class MatchLineup(MatchLineupBase):
    id: str

    class Config:
        from_attributes = True
