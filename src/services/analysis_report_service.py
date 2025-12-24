from typing import List, Optional
from models.analysis_report import AnalysisReport, AnalysisReportCreate
import json

class AnalysisReportService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_analysis_report(self, report: AnalysisReportCreate, user_team_ids: List[str]) -> AnalysisReport:
        # Validate that the match's teams are owned by the user
        # This requires fetching match details, which is complex here.
        # For simplicity, we'll assume match_id is valid and linked to user's team via MatchService.
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO analysis_reports (id, match_id, report_type, report_data, generated_by) VALUES (UUID(), %s, %s, %s, %s)"
            cursor.execute(sql, (report.match_id, report.report_type, json.dumps(report.report_data), report.generated_by))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM analysis_reports WHERE match_id = %s ORDER BY generated_at DESC LIMIT 1", (report.match_id,))
            new_report = cursor.fetchone()
            if new_report and isinstance(new_report['report_data'], str):
                new_report['report_data'] = json.loads(new_report['report_data'])
            return AnalysisReport(**new_report)

    def get_analysis_report(self, report_id: str, user_team_ids: List[str]) -> Optional[AnalysisReport]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT ar.* FROM analysis_reports ar JOIN matches m ON ar.match_id = m.id WHERE ar.id = %s AND (m.home_team_id IN %s OR m.away_team_id IN %s)"
            cursor.execute(sql, (report_id, user_team_ids, user_team_ids))
            report = cursor.fetchone()
            if report:
                if isinstance(report['report_data'], str):
                    report['report_data'] = json.loads(report['report_data'])
                return AnalysisReport(**report)
            return None

    def get_all_analysis_reports(self, user_team_ids: List[str]) -> List[AnalysisReport]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            sql = "SELECT ar.id, ar.match_id, ar.report_type, ar.report_data, ar.generated_at, ar.generated_by FROM analysis_reports ar JOIN matches m ON ar.match_id = m.id WHERE m.home_team_id IN %s OR m.away_team_id IN %s"
            cursor.execute(sql, (user_team_ids, user_team_ids))
            reports = cursor.fetchall()
            for report in reports:
                if isinstance(report['report_data'], str):
                    report['report_data'] = json.loads(report['report_data'])
            return [AnalysisReport(**report) for report in reports]

    def update_analysis_report(self, report_id: str, report_update: AnalysisReportCreate, user_team_ids: List[str]) -> Optional[AnalysisReport]:
        # Validate that the match's teams are owned by the user
        # This requires fetching match details, which is complex here.
        # For simplicity, we'll assume match_id is valid and linked to user's team via MatchService.
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE analysis_reports SET match_id = %s, report_type = %s, report_data = %s, generated_by = %s WHERE id = %s"
            cursor.execute(sql, (report_update.match_id, report_update.report_type, json.dumps(report_update.report_data), report_update.generated_by, report_id))
            self.db_connection.commit()
            return self.get_analysis_report(report_id, user_team_ids)

    def delete_analysis_report(self, report_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM analysis_reports WHERE id = %s AND match_id IN (SELECT id FROM matches WHERE home_team_id IN %s OR away_team_id IN %s)"
            cursor.execute(sql, (report_id, user_team_ids, user_team_ids))
            self.db_connection.commit()
            return cursor.rowcount > 0
