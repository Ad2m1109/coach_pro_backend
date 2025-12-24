from typing import List, Optional
from models.event import Event, EventCreate

class EventService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_event(self, event: EventCreate, user_team_ids: List[str]) -> Event:
        # Events are not directly linked to teams in the model, 
        # but if they were, we'd validate user_team_ids here.
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO events (id, name) VALUES (UUID(), %s)"
            cursor.execute(sql, (event.name,))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM events WHERE name = %s ORDER BY created_at DESC LIMIT 1", (event.name,))
            new_event = cursor.fetchone()
            return Event(**new_event)

    def get_event(self, event_id: str, user_team_ids: List[str]) -> Optional[Event]:
        # Events are not directly linked to teams in the model, 
        # but if they were, we'd validate user_team_ids here.
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM events WHERE id = %s"
            cursor.execute(sql, (event_id,))
            event = cursor.fetchone()
            if event:
                return Event(**event)
            return None

    def get_all_events(self, user_team_ids: List[str]) -> List[Event]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            # Events are not directly linked to teams in the model, 
            # so we return all events. If events should be team-specific,
            # the model needs a team_id.
            sql = "SELECT * FROM events"
            cursor.execute(sql)
            events = cursor.fetchall()
            return [Event(**e) for e in events]

    def update_event(self, event_id: str, event_update: EventCreate, user_team_ids: List[str]) -> Optional[Event]:
        # Events are not directly linked to teams in the model, 
        # but if they were, we'd validate user_team_ids here.
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE events SET name = %s WHERE id = %s"
            cursor.execute(sql, (event_update.name, event_id))
            self.db_connection.commit()
            return self.get_event(event_id, user_team_ids)

    def delete_event(self, event_id: str, user_team_ids: List[str]) -> bool:
        # Events are not directly linked to teams in the model, 
        # but if they were, we'd validate user_team_ids here.
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM events WHERE id = %s"
            cursor.execute(sql, (event_id,))
            self.db_connection.commit()
            return cursor.rowcount > 0