from typing import List, Optional
from models.staff import Staff, StaffCreate

class StaffService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_staff(self, staff: StaffCreate, user_team_ids: List[str]) -> Staff:
        if staff.team_id not in user_team_ids:
            raise ValueError("Team not owned by current user.")
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO staff (id, team_id, name, role) VALUES (UUID(), %s, %s, %s)"
            cursor.execute(sql, (staff.team_id, staff.name, staff.role.value if staff.role else None))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM staff WHERE name = %s ORDER BY id DESC LIMIT 1", (staff.name,))
            new_staff = cursor.fetchone()
            return Staff(**new_staff)

    def get_staff(self, staff_id: str, user_team_ids: List[str]) -> Optional[Staff]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM staff WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (staff_id, user_team_ids))
            staff = cursor.fetchone()
            if staff:
                return Staff(**staff)
            return None

    def get_all_staff(self, user_team_ids: List[str]) -> List[Staff]:
        if not user_team_ids:
            return []
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM staff WHERE team_id IN %s"
            cursor.execute(sql, (user_team_ids,))
            staff = cursor.fetchall()
            return [Staff(**s) for s in staff]

    def update_staff(self, staff_id: str, staff_update: StaffCreate, user_team_ids: List[str]) -> Optional[Staff]:
        if staff_update.team_id not in user_team_ids:
            raise ValueError("Team not owned by current user.")
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE staff SET team_id = %s, name = %s, role = %s WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (staff_update.team_id, staff_update.name, staff_update.role.value if staff_update.role else None, staff_id, user_team_ids))
            self.db_connection.commit()
            return self.get_staff(staff_id, user_team_ids)

    def delete_staff(self, staff_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM staff WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (staff_id, user_team_ids))
            self.db_connection.commit()
            return cursor.rowcount > 0
