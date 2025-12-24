from pydantic import BaseModel
from typing import List, Optional
from .match import Match
from .match_lineup import MatchLineup
from .player_match_statistics import PlayerMatchStatistics
from .match_team_statistics import MatchTeamStatistics
from .match_event import MatchEvent
from .formation import Formation
from .player import Player

class PlayerWithPosition(Player):
    position_in_formation: Optional[str] = None

class TeamLineup(BaseModel):
    team_id: str
    team_name: str
    formation: Optional[Formation] = None
    players: List[PlayerWithPosition]

class MatchDetails(BaseModel):
    match_info: Match
    home_lineup: TeamLineup
    away_lineup: TeamLineup
    events: List[MatchEvent]
    player_stats: List[PlayerMatchStatistics]
    team_stats: List[MatchTeamStatistics]
