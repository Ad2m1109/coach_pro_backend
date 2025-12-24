from typing import List, Optional
from models.match_event import MatchEvent, MatchEventCreate

class MatchEventService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_match_event(self, event: MatchEventCreate) -> MatchEvent:
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO match_events (id, match_id, player_id, event_type, minute, video_timestamp, coordinates) VALUES (UUID(), %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (event.match_id, event.player_id, event.event_type.value, event.minute, event.video_timestamp, event.coordinates))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM match_events WHERE match_id = %s AND player_id = %s AND event_type = %s AND minute = %s ORDER BY id DESC LIMIT 1", (event.match_id, event.player_id, event.event_type.value, event.minute))
            new_event = cursor.fetchone()
            return MatchEvent(**new_event)

    def get_match_event(self, event_id: str) -> Optional[MatchEvent]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM match_events WHERE id = %s"
            cursor.execute(sql, (event_id,))
            event = cursor.fetchone()
            if event:
                return MatchEvent(**event)
            return None

    def get_all_match_events(self, match_id: str = None) -> List[MatchEvent]:
        with self.db_connection.cursor() as cursor:
            if match_id:
                sql = "SELECT * FROM match_events WHERE match_id = %s ORDER BY minute ASC"
                cursor.execute(sql, (match_id,))
            else:
                sql = "SELECT * FROM match_events ORDER BY minute ASC"
                cursor.execute(sql)
            events = cursor.fetchall()
            return [MatchEvent(**e) for e in events]

    def update_match_event(self, event_id: str, event_update: MatchEventCreate) -> Optional[MatchEvent]:
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE match_events SET match_id = %s, player_id = %s, event_type = %s, minute = %s, video_timestamp = %s, coordinates = %s WHERE id = %s"
            cursor.execute(sql, (event_update.match_id, event_update.player_id, event_update.event_type.value, event_update.minute, event_update.video_timestamp, event_update.coordinates, event_id))
            self.db_connection.commit()
            return self.get_match_event(event_id)

    def delete_match_event(self, event_id: str) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM match_events WHERE id = %s"
            cursor.execute(sql, (event_id,))
            self.db_connection.commit()
            return cursor.rowcount > 0
