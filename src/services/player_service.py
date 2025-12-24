from typing import List, Optional
from models.player import Player, PlayerCreate
from fastapi import UploadFile
import os
import shutil
import uuid

class PlayerService:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_player(self, player: PlayerCreate, user_team_ids: List[str]) -> Player:
        if player.team_id not in user_team_ids:
            raise ValueError("Team not owned by current user.")
        with self.db_connection.cursor() as cursor:
            sql = "INSERT INTO players (id, team_id, name, position, jersey_number, birth_date, dominant_foot, height_cm, weight_kg, nationality, country_code, image_url, market_value) VALUES (UUID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (player.team_id, player.name, player.position.value if player.position else None, player.jersey_number, player.birth_date, player.dominant_foot.value if player.dominant_foot else None, player.height_cm, player.weight_kg, player.nationality, player.country_code, player.image_url, player.market_value))
            self.db_connection.commit()
            cursor.execute("SELECT * FROM players WHERE name = %s ORDER BY id DESC LIMIT 1", (player.name,))
            new_player = cursor.fetchone()
            return Player(**new_player)

    def get_player(self, player_id: str, user_team_ids: List[str]) -> Optional[Player]:
        with self.db_connection.cursor() as cursor:
            sql = "SELECT * FROM players WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (player_id, user_team_ids))
            player = cursor.fetchone()
            if player:
                return Player(**player)
            return None

    def get_all_players(self, user_team_ids: List[str]) -> List[Player]:
        if not user_team_ids:
            return [] # No teams, no players
        with self.db_connection.cursor() as cursor:
            # Using a tuple for IN clause
            sql = "SELECT * FROM players WHERE team_id IN %s"
            cursor.execute(sql, (user_team_ids,))
            players = cursor.fetchall()
            return [Player(**player) for player in players]

    def update_player(self, player_id: str, player_update: PlayerCreate, user_team_ids: List[str]) -> Optional[Player]:
        if player_update.team_id not in user_team_ids:
            raise ValueError("Team not owned by current user.")
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE players SET team_id = %s, name = %s, position = %s, jersey_number = %s, birth_date = %s, dominant_foot = %s, height_cm = %s, weight_kg = %s, nationality = %s, country_code = %s, image_url = %s WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (player_update.team_id, player_update.name, player_update.position.value if player_update.position else None, player_update.jersey_number, player_update.birth_date, player_update.dominant_foot.value if player_update.dominant_foot else None, player_update.height_cm, player_update.weight_kg, player_update.nationality, player_update.country_code, player_update.image_url, player_id, user_team_ids))
            self.db_connection.commit()
            return self.get_player(player_id, user_team_ids)

    def delete_player(self, player_id: str, user_team_ids: List[str]) -> bool:
        with self.db_connection.cursor() as cursor:
            sql = "DELETE FROM players WHERE id = %s AND team_id IN %s"
            cursor.execute(sql, (player_id, user_team_ids))
            self.db_connection.commit()
            return cursor.rowcount > 0

    def save_player_image(self, player_id: str, file: UploadFile, user_team_ids: List[str]) -> Player:
        # Define the path to save the image
        upload_dir = "static/images/players"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a unique filename to prevent conflicts
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{player_id}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Construct the URL to access the file
        # This URL depends on your server's address and the static path
        # Assuming the server is running on http://localhost:8000
        image_url = f"/static/images/players/{unique_filename}"

        # Update the player's image_url in the database
        with self.db_connection.cursor() as cursor:
            sql = "UPDATE players SET image_url = %s WHERE id = %s"
            cursor.execute(sql, (image_url, player_id))
            self.db_connection.commit()

        # Return the updated player object
        return self.get_player(player_id, user_team_ids)
