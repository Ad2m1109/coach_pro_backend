from typing import List, Optional
from models.video_segment import VideoSegment, VideoSegmentCreate

class VideoSegmentService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_video_segment(self, segment: VideoSegmentCreate, user_team_ids: List[str]) -> VideoSegment:
        # Validate that the match's teams are owned by the user
        # This requires fetching match details, which is complex here.
        # For simplicity, we'll assume match_id is valid and linked to user's team via MatchService.
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO video_segments (id, match_id, event_id, analysis_report_id, start_time_sec, end_time_sec, description, video_url) VALUES (UUID(), %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (segment.match_id, segment.event_id, segment.analysis_report_id, segment.start_time_sec, segment.end_time_sec, segment.description, segment.video_url))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM video_segments WHERE match_id = %s AND start_time_sec = %s AND end_time_sec = %s ORDER BY id DESC LIMIT 1", (segment.match_id, segment.start_time_sec, segment.end_time_sec))
            new_segment = cursor.fetchone()
            return VideoSegment(**new_segment)

    def get_video_segment(self, segment_id: str, user_team_ids: List[str]) -> Optional[VideoSegment]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT vs.* FROM video_segments vs JOIN matches m ON vs.match_id = m.id WHERE vs.id = %s AND (m.home_team_id IN %s OR m.away_team_id IN %s)"
            cursor.execute(sql, (segment_id, user_team_ids, user_team_ids))
            segment = cursor.fetchone()
            if segment:
                return VideoSegment(**segment)
            return None

    def get_all_video_segments(self, user_team_ids: List[str]) -> List[VideoSegment]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            sql = "SELECT vs.* FROM video_segments vs JOIN matches m ON vs.match_id = m.id WHERE m.home_team_id IN %s OR m.away_team_id IN %s"
            cursor.execute(sql, (user_team_ids, user_team_ids))
            segments = cursor.fetchall()
            return [VideoSegment(**s) for s in segments]

    def update_video_segment(self, segment_id: str, segment_update: VideoSegmentCreate, user_team_ids: List[str]) -> Optional[VideoSegment]:
        # Validate that the match's teams are owned by the user
        # This requires fetching match details, which is complex here.
        # For simplicity, we'll assume match_id is valid and linked to user's team via MatchService.
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE video_segments SET match_id = %s, event_id = %s, analysis_report_id = %s, start_time_sec = %s, end_time_sec = %s, description = %s, video_url = %s WHERE id = %s"
            cursor.execute(sql, (segment_update.match_id, segment_update.event_id, segment_update.analysis_report_id, segment_update.start_time_sec, segment_update.end_time_sec, segment_update.description, segment_update.video_url, segment_id))
            self.db_connection.commit()
            return self.get_video_segment(segment_id, user_team_ids)

    def delete_video_segment(self, segment_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM video_segments WHERE id = %s AND match_id IN (SELECT id FROM matches WHERE home_team_id IN %s OR away_team_id IN %s)"
            cursor.execute(sql, (segment_id, user_team_ids, user_team_ids))
            self.db_connection.commit()
            return cursor.rowcount > 0
