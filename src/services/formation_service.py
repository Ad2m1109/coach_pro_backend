import json
from typing import List, Optional
from models.formation import Formation, FormationCreate

class FormationService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _to_model(self, data: dict) -> Optional[Formation]:
        if not data:
            return None
        if 'positions' in data and isinstance(data['positions'], str):
            try:
                data['positions'] = json.loads(data['positions'])
            except json.JSONDecodeError:
                data['positions'] = None
        return Formation(**data)

    def create_formation(self, formation: FormationCreate, user_id: str) -> Formation:
        with self.db_connection.cursor() as cursor:
            positions_json = json.dumps(formation.positions) if formation.positions is not None else None
            sql = "INSERT INTO formations (id, name, description, positions, user_id) VALUES (UUID(), %s, %s, %s, %s)"
            cursor.execute(sql, (formation.name, formation.description, positions_json, user_id))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM formations WHERE name = %s AND user_id = %s ORDER BY created_at DESC LIMIT 1", (formation.name, user_id))
            new_formation = cursor.fetchone()
            return self._to_model(new_formation)

    def get_formation(self, formation_id: str, user_id: str) -> Optional[Formation]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM formations WHERE id = %s AND (user_id = %s OR user_id IS NULL)"
            cursor.execute(sql, (formation_id, user_id))
            formation = cursor.fetchone()
            return self._to_model(formation)

    def get_all_formations(self, user_id: str) -> List[Formation]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM formations WHERE user_id = %s OR user_id IS NULL"
            cursor.execute(sql, (user_id,))
            formations = cursor.fetchall()
            return [self._to_model(f) for f in formations]

    def update_formation(self, formation_id: str, formation_update: FormationCreate, user_id: str) -> Optional[Formation]:
        with self.db_connection.cursor() as cursor:
            positions_json = json.dumps(formation_update.positions) if formation_update.positions is not None else None
            sql = "UPDATE formations SET name = %s, description = %s, positions = %s WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (formation_update.name, formation_update.description, positions_json, formation_id, user_id))
            self.db_connection.commit()
            if cursor.rowcount == 0:
                return None
            return self.get_formation(formation_id, user_id)

    def delete_formation(self, formation_id: str, user_id: str) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM formations WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (formation_id, user_id))
            self.db_connection.commit()
            return cursor.rowcount > 0
