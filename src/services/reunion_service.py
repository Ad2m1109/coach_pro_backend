from typing import List
from models.reunion import Reunion, ReunionCreate
from datetime import datetime

class ReunionService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_all_reunions(self, user_team_ids: List[str]) -> List[Reunion]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            # Assuming reunions are linked to a team, or a user's context
            # For now, we'll return all, but in a real app, this would be filtered.
            # This service doesn't have a direct team_id link in the Reunion model.
            # If Reunion should be team-specific, the model needs a team_id.
            # For now, we'll just return all, but keep user_team_ids for consistency.
            sql = "SELECT id, title, date, location, icon_name FROM reunions"
            cursor.execute(sql)
            reunions_data = cursor.fetchall()
            return [Reunion(**r) for r in reunions_data]

    def create_reunion(self, reunion: ReunionCreate, user_team_ids: List[str]) -> Reunion:
        # Assuming reunion is not directly linked to a team in the model, 
        # but if it were, we'd validate user_team_ids here.
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO reunions (id, title, date, location, icon_name) VALUES (UUID(), %s, %s, %s, %s)"
            cursor.execute(sql, (reunion.title, reunion.date, reunion.location, reunion.icon_name))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM reunions WHERE title = %s ORDER BY created_at DESC LIMIT 1", (reunion.title,))
            new_reunion = cursor.fetchone()
            return Reunion(**new_reunion)

    def delete_reunion(self, reunion_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            # Assuming reunion is not directly linked to a team in the model, 
            # but if it were, we'd validate user_team_ids here.
            sql = "DELETE FROM reunions WHERE id = %s"
            cursor.execute(sql, (reunion_id,))
            self.db_connection.commit()
            return cursor.rowcount > 0
