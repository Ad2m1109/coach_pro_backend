from typing import List, Optional
from models.match_lineup import MatchLineup, MatchLineupCreate

class MatchLineupService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_match_lineup(self, lineup: MatchLineupCreate, user_team_ids: List[str]) -> MatchLineup:
        if lineup.team_id not in user_team_ids:
            raise ValueError("Team not owned by current user.")
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO match_lineups (id, match_id, team_id, formation_id, is_starting, player_id, position_in_formation) VALUES (UUID(), %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (lineup.match_id, lineup.team_id, lineup.formation_id, lineup.is_starting, lineup.player_id, lineup.position_in_formation))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM match_lineups WHERE match_id = %s AND team_id = %s AND player_id = %s ORDER BY id DESC LIMIT 1", (lineup.match_id, lineup.team_id, lineup.player_id))
            new_lineup = cursor.fetchone()
            return MatchLineup(**new_lineup)

    def get_match_lineup(self, lineup_id: str, user_team_ids: List[str]) -> Optional[MatchLineup]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT ml.* FROM match_lineups ml JOIN matches m ON ml.match_id = m.id WHERE ml.id = %s AND (m.home_team_id IN %s OR m.away_team_id IN %s)"
            cursor.execute(sql, (lineup_id, user_team_ids, user_team_ids))
            lineup = cursor.fetchone()
            if lineup:
                return MatchLineup(**lineup)
            return None

    def get_all_match_lineups(self, user_team_ids: List[str], match_id: str = None) -> List[MatchLineup]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            sql = """
                SELECT ml.* FROM match_lineups ml
                JOIN matches m ON ml.match_id = m.id
                WHERE (m.home_team_id IN %s OR m.away_team_id IN %s)
            """
            params = [user_team_ids, user_team_ids]
            if match_id:
                sql += " AND ml.match_id = %s"
                params.append(match_id)
            
            cursor.execute(sql, tuple(params))
            lineups = cursor.fetchall()
            return [MatchLineup(**lineup_data) for lineup_data in lineups]

    def update_match_lineup(self, lineup_id: str, lineup_update: MatchLineupCreate, user_team_ids: List[str]) -> Optional[MatchLineup]:
        if lineup_update.team_id not in user_team_ids:
            raise ValueError("Team not owned by current user.")
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE match_lineups SET match_id = %s, team_id = %s, formation_id = %s, is_starting = %s, player_id = %s, position_in_formation = %s WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (lineup_update.match_id, lineup_update.team_id, lineup_update.formation_id, lineup_update.is_starting, lineup_update.player_id, lineup_update.position_in_formation, lineup_id, user_team_ids))
            self.db_connection.commit()
            return self.get_match_lineup(lineup_id, user_team_ids)

    def delete_match_lineup(self, lineup_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM match_lineups WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (lineup_id, user_team_ids))
            self.db_connection.commit()
            return cursor.rowcount > 0
