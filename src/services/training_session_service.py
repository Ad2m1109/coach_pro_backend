from typing import List
from models.training_session import TrainingSession, TrainingSessionCreate
from datetime import datetime

class TrainingSessionService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_all_training_sessions(self, user_team_ids: List[str]) -> List[TrainingSession]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            # Assuming training sessions are linked to a team, or a user's context
            # For now, we'll return all, but in a real app, this would be filtered.
            # This service doesn't have a direct team_id link in the TrainingSession model.
            # If TrainingSession should be team-specific, the model needs a team_id.
            # For now, we'll just return all, but keep user_team_ids for consistency.
            sql = "SELECT id, title, date, focus, icon_name FROM training_sessions"
            cursor.execute(sql)
            sessions_data = cursor.fetchall()
            return [TrainingSession(**s) for s in sessions_data]

    def create_training_session(self, session: TrainingSessionCreate, user_team_ids: List[str]) -> TrainingSession:
        # Assuming training session is not directly linked to a team in the model, 
        # but if it were, we'd validate user_team_ids here.
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO training_sessions (id, title, date, focus, icon_name) VALUES (UUID(), %s, %s, %s, %s)"
            cursor.execute(sql, (session.title, session.date, session.focus, session.icon_name))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM training_sessions WHERE title = %s ORDER BY created_at DESC LIMIT 1", (session.title,))
            new_session = cursor.fetchone()
            return TrainingSession(**new_session)

    def delete_training_session(self, session_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            # Assuming training session is not directly linked to a team in the model, 
            # but if it were, we'd validate user_team_ids here.
            sql = "DELETE FROM training_sessions WHERE id = %s"
            cursor.execute(sql, (session_id,))
            self.db_connection.commit()
            return cursor.rowcount > 0
